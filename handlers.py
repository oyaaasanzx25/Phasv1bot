import logging
from telegram import Update
from telegram.ext import ContextTypes
from google import genai
from google.genai import types
import config

logger = logging.getLogger(__name__)

# Inisialisasi Gemini Client
client = genai.Client(api_key=config.GEMINI_API_KEY)

SYSTEM_INSTRUCTION = (
    "Kamu adalah PhasBot, asisten keamanan Telegram & AI cerdas. "
    "Tugas utamamu adalah membantu pengguna, menjaga dari spam/scam, dan menjawab pertanyaan. "
    "Gunakan bahasa Indonesia yang jelas, ramah, dan profesional."
)

# Kata kunci berpotensi scam/promosi berbahaya
SCAM_KEYWORDS = [
    "investasi garansi", "bonus 100%", "menang undian", 
    "klaim saldo free", "dapat duit cepat", "deposit murah"
]

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    welcome_text = (
        f"Halo <b>{user.mention_html()}</b>! 👋\n\n"
        "Selamat datang di <b>PhasBot</b>!\n"
        "Saya adalah bot penjaga dari Spam/Scam yang didukung oleh Gemini AI.\n\n"
        "📌 <b>Fitur Utama:</b>\n"
        "• Ngobrol santai & tanya jawab dengan AI\n"
        "• Deteksi pesan/link indikasi scam (`/check <teks/link>`)\n"
        "• Filter otomatis kata kunci mencurigakan"
    )
    await update.message.reply_html(welcome_text)

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "<b>📌 Daftar Perintah PhasBot:</b>\n\n"
        "/start - Memulai ulang bot\n"
        "/help - Menampilkan bantuan ini\n"
        "/check &lt;teks/link&gt; - Analisis teks atau link apakah terindikasi scam\n\n"
        "<i>Kirim pesan biasa untuk mengobrol langsung dengan Gemini AI!</i>"
    )
    await update.message.reply_html(help_text)

async def check_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menganalisis indikasi scam/phishing menggunakan Gemini AI."""
    if not context.args:
        await update.message.reply_text("⚠️ Harap masukkan teks atau link setelah perintah /check.\n\nContoh: `/check http://link-hadiah.com`", parse_mode="Markdown")
        return

    query = " ".join(context.args)
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    prompt = (
        f"Analisis teks/link berikut apakah berpotensi SPAM, SCAM, PHISHING, atau AMAN:\n\n"
        f"'{query}'\n\n"
        f"Berikan penjelasannya secara singkat, padat, dan berikan kesimpulan akhir (AMAN / WASPADA / BAHAYA)."
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
        )
        await update.message.reply_text(f"🔍 <b>Hasil Analisis Keamanan:</b>\n\n{response.text}", parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error pada /check: {e}")
        await update.message.reply_text("⚠️ Gagal melakukan analisis keamanan saat ini.")

async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler obrolan AI & deteksi spam otomatis."""
    user_text = update.message.text
    user_text_lower = user_text.lower()

    # 1. Filter dasar anti-spam kata kunci
    if any(keyword in user_text_lower for keyword in SCAM_KEYWORDS):
        await update.message.reply_text(
            "⚠️ <b>Peringatan Sistem Anti-Spam:</b>\n"
            "Pesan kamu terindikasi mengandung pola promosi/scam mencurigakan. Harap berhati-hati!",
            parse_mode="HTML"
        )
        return

    # 2. Respon dengan Gemini AI
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
            )
        )
        reply = response.text if response.text else "Maaf, saya tidak bisa memproses balasan saat ini."
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"Error Gemini Chat: {e}")
        await update.message.reply_text("⚠️ Terjadi gangguan pada koneksi AI.")
