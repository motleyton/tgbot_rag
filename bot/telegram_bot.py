import datetime

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, \
    filters, ContextTypes, CallbackContext

from database_helper import Database
from utils import error_handler
from openai_helper import localized_text, OpenAI

class ChatGPTTelegramBot:

    def __init__(self, config: dict, openai: OpenAI):
        self.config = config
        self.openai = openai
        self.db = Database(config)


    async def start(self, update: Update, context: CallbackContext) -> None:

        await update.message.reply_text("Привет! Меня зовут Blacky, я нейроконсультант языковой студии Welcome. Помогу Менеджеру по работе с клиентами, дам ответ на любой вопрос в вашей зоне ответственности (кроме работы в Талланто)")

    async def help(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        bot_language = self.config['bot_language']
        help_text = (
            localized_text('help_text', bot_language)[0]
        )
        await update.message.reply_text(help_text, disable_web_page_preview=True)

    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_message = update.message.text
        qa_chain = self.openai.initialize_chat()
        response = qa_chain.run(user_message)
        await update.message.reply_text(response)



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
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.message_handler))
        application.add_error_handler(error_handler)

        application.run_polling()