import logging
import os
import openai
import json

from langchain.chains import LLMChain, RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.vectorstores import FAISS
from telegram import Update

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
        # return key as text
        return key


class OpenAI:
    def __init__(self, config: dict):
        """
        Initializes the OpenAI helper class with the given configuration.
        :param config: A dictionary containing the GPT configuration
        """
        openai.api_key = config['api_key']
        # openai.proxy = config['proxy']
        self.config = config
        self.model_name = config['model']
        self.system_prompt = config['system_prompt']
        self.db = Database(config)
        self.temperature = config['temperature']


    def initialize_chat(self):
        llm = ChatOpenAI(
            temperature=self.temperature,
            openai_api_key=openai.api_key,
            model_name=self.model_name,
        )
        embeddings = OpenAIEmbeddings(openai_api_key=openai.api_key)
        texts = self.db.open_database()
        db = FAISS.from_documents(texts, embeddings)
        db.as_retriever()
        db.save_local('faiss_index')

        template = '''
        Ответь на вопрос используя {text_input}. Отвечай на русском языке
        '''

        prompt = PromptTemplate(
            input_variables=["text_input"],
            template=template
        )

        chain = LLMChain(llm=llm, prompt=prompt)

        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=db.as_retriever()
        )

        return chain, qa










