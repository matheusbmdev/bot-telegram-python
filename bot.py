import logging
import requests
from telegram import __version__ as TG_VER
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
import os
from dotenv import load_dotenv

load_dotenv() 

TELEGRAM_API_TOKEN= os.getenv("TELEGRAM_API_TOKEN")
SERVER_URL=os.getenv("SERVER_URL")

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 5):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

GENDER = range(1)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    # reply_keyboard = [["Boy", "Girl", "Other"]]

    # await update.message.reply_text(
    #     "Hi! My name is Professor Bot. I will hold a conversation with you. "
    #     "Send /cancel to stop talking to me.\n\n"
    #     "Are you a boy or a girl?",
    #     reply_markup=ReplyKeyboardMarkup(
    #         reply_keyboard, one_time_keyboard=True, input_field_placeholder="Boy or Girl?"
    #     ),
    # )
    message = update.message.text
    context.bot.send_message(chat_id=update.effective_chat.id, text="Processando mensagem...")
    chat_id = update.effective_chat.id  # Obter o chat_id da conversa atual
    # Chame o endpoint do servidor FastAPI para processar a conversa
    response = requests.post(f"{SERVER_URL}/conversation",  json={"message": message, "chat_id": chat_id},)
    if response.status_code == 200:
        update.message.reply_text("Mensagem processada com sucesso!")
    else:
        update.message.reply_text("Erro ao processar mensagem.")

    return GENDER


async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    logger.info("Gender of %s: %s", user.first_name, update.message.text)
    await update.message.reply_text(
        "I see! Please send me a photo of yourself, "
        "so I know what you look like, or send /skip if you don't want to.",
        reply_markup=ReplyKeyboardRemove(),
    )

    ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GENDER: [MessageHandler(filters.Regex("^(Boy|Girl|Other)$"), gender)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()