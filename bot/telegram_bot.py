import datetime

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, \
    filters, ContextTypes, CallbackContext

from auth import authenticate_google_api
from database_helper import Database
from utils import error_handler
from openai_helper import localized_text, OpenAI

class ChatGPTTelegramBot:

    def __init__(self, config: dict, openai: OpenAI):
        self.config = config
        self.openai = openai
        self.db = Database(config)
        self.allowed_usernames = config['allowed_usernames']


    async def start(self, update: Update, context: CallbackContext) -> None:
        bot_language = self.config['bot_language']
        username = "@" + update.message.from_user.username if update.message.from_user.username else None
        disallowed = (
            localized_text('disallowed', bot_language))
        if username not in self.allowed_usernames:
            await update.message.reply_text(disallowed, disable_web_page_preview=True)
            return

        start_keyboard = [['/start', '/help', '/update_database']]
        reply_markup = ReplyKeyboardMarkup(start_keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("Привет! Меня зовут Blacky, я нейроконсультант языковой студии Welcome. "
                                        "Помогу Менеджеру по работе с клиентами, дам ответ на любой вопрос в вашей зоне ответственности (кроме работы в Талланто)",
                                        reply_markup=reply_markup)

    async def help(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        username = "@" + update.message.from_user.username if update.message.from_user.username else None
        bot_language = self.config['bot_language']
        disallowed = (
            localized_text('disallowed', bot_language))
        if username not in self.allowed_usernames:
            await update.message.reply_text(disallowed, disable_web_page_preview=True)
            return

        help_text = (
            localized_text('help_text', bot_language)[0]
        )
        await update.message.reply_text(help_text, disable_web_page_preview=True)

    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_message = update.message.text
        qa_chain = self.openai.initialize_chat()
        response = qa_chain.run(user_message)
        await update.message.reply_text(response)

    async def update_database(self, update: Update, context: CallbackContext) -> None:
        username = "@" + update.message.from_user.username if update.message.from_user.username else None
        bot_language = self.config['bot_language']
        disallowed = (
            localized_text('disallowed', bot_language))
        if username not in self.allowed_usernames:
            await update.message.reply_text(disallowed, disable_web_page_preview=True)
            return

        try:
            # Здесь вызываем функцию аутентификации перед обновлением базы данных
            authenticate_google_api(self.config['credentials_path'], self.config['token_path'],  scopes=['https://www.googleapis.com/auth/drive'])

            new_db, new_template = self.db.open_database()
            self.openai.reload_database(new_db, new_template)

            await update.message.reply_text("База данных успешно обновлена!")
        except Exception as e:
            print(e)
            await update.message.reply_text(f"Произошла ошибка при обновлении базы данных")


    def run(self):
        """
        Runs the bot indefinitely until the user presses Ctrl+C
        """

        application = ApplicationBuilder() \
            .token(self.config['token']) \
            .concurrent_updates(True) \
            .build()

        application.add_handler(CommandHandler('start', self.start))
        application.add_handler(CommandHandler('help', self.help))
        application.add_handler(CommandHandler('update_database', self.update_database))

        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.message_handler))
        application.add_error_handler(error_handler)

        application.run_polling()