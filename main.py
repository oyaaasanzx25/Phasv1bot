import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
import config
import handlers

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

async def global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Terjadi exception pada update:", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ Maaf, terjadi kesalahan internal pada sistem."
        )

def main() -> None:
    app = Application.builder().token(config.TOKEN).build()

    # Handlers Perintah
    app.add_handler(CommandHandler("start", handlers.start_handler))
    app.add_handler(CommandHandler("help", handlers.help_handler))
    app.add_handler(CommandHandler("check", handlers.check_handler))

    # Handler Pesan Obrolan & Anti-Spam
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.chat_handler))

    app.add_error_handler(global_error_handler)

    logger.info("PhasBot sedang berjalan...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
