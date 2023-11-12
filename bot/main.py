import logging
import os
from dotenv import load_dotenv
from openai_helper import OpenAI
from telegram_bot import ChatGPTTelegramBot


def main():
    # Read .env file
    load_dotenv()

    # Setup logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    # Check if the required environment variables are set
    required_values = ['TELEGRAM_BOT_TOKEN', 'OPENAI_API_KEY']
    if missing_values := [
        value for value in required_values if os.environ.get(value) is None
    ]:
        logging.error(f'The following environment values are missing in your .env: {", ".join(missing_values)}')
        exit(1)

    # Setup configurations
    model = os.environ.get('OPENAI_MODEL')
    openai_config = {
        'folder_id': os.environ['FOLDER_ID'],
        'prompt_id': os.environ['PROMPT_ID'],
        'api_key': os.environ['OPENAI_API_KEY'],

        'max_history_size': int(os.environ.get('MAX_HISTORY_SIZE', 15)),
        'system_prompt': os.environ.get('SYSTEM_PROMPT'),
        'temperature': float(os.environ.get('TEMPERATURE', 0)),
        'model': model,
    }

    # log deprecation warning for old budget variable names
    # old variables are caught in the telegram_config definition for now
    # remove support for old budget names at some point in the future
    if os.environ.get('MONTHLY_USER_BUDGETS') is not None:
        logging.warning('The environment variable MONTHLY_USER_BUDGETS is deprecated. '
                        'Please use USER_BUDGETS with BUDGET_PERIOD instead.')
    if os.environ.get('MONTHLY_GUEST_BUDGET') is not None:
        logging.warning('The environment variable MONTHLY_GUEST_BUDGET is deprecated. '
                        'Please use GUEST_BUDGET with BUDGET_PERIOD instead.')

    telegram_config = {
        'token': os.environ['TELEGRAM_BOT_TOKEN'],
        'bot_language': os.environ.get('BOT_LANGUAGE'),
        'folder_id': os.environ['FOLDER_ID'],

    }

    # Setup and run ChatGPT and Telegram bot
    openai = OpenAI(config=openai_config)
    telegram_bot = ChatGPTTelegramBot(config=telegram_config, openai=openai)
    telegram_bot.run()


if __name__ == '__main__':
    main()