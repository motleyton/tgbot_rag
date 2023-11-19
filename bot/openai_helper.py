import logging
import os
import openai
import json

from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

from langchain.prompts import PromptTemplate


from database_helper import Database
# Load translations
parent_dir_path = os.path.join(os.path.dirname(__file__), os.pardir)
translations_file_path = os.path.join(parent_dir_path, 'translations.json')
with open(translations_file_path, 'r', encoding='utf-8') as f:
    translations = json.load(f)


def localized_text(key, bot_language):
    """
    Return translated text for a key in specified bot_language.
    Keys and translations can be found in the translations.json.
    """
    try:
        return translations[bot_language][key]
    except KeyError:
        logging.warning(f"No translation available for bot_language code '{bot_language}' and key '{key}'")
        if key in translations['en']:
            return translations['en'][key]
        logging.warning(f"No english definition found for key '{key}' in translations.json")
        return key


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OpenAI:
    def __init__(self, config: dict):
        """
        Initializes the OpenAI helper class with the given configuration.
        :param config: A dictionary containing the GPT configuration
        """
        openai.api_key = config['api_key']
        self.config = config
        self.model_name = config['model']
        self.db_instance = Database(config)
        self.db, self.template = self.db_instance.open_database()
        self.temperature = config['temperature']

    def reload_database(self, new_db, new_template):
        """
        Updates the database and template in OpenAI instance.
        """
        self.db = new_db
        self.template = new_template


    def initialize_chat(self):
        llm = ChatOpenAI(
            temperature=self.temperature,
            openai_api_key=openai.api_key,
            model_name=self.model_name,
        )

        template = '''Используй данные из контекста, чтобы предоставить точный и информативный ответ.
                    Мои ответы будут строго основаны на данных, без добавления какой-либо выдуманной информации.
                    {context}

                    Вопрос: {question}
                    '''

        prompt = PromptTemplate(
            template=self.template, input_variables=["question", "context"]
        )
        chain_type_kwargs = {"prompt": prompt, 'verbose': False}

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.db.as_retriever(),
            chain_type_kwargs=chain_type_kwargs
        )
        return qa_chain







