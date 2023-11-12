import logging
import os
import openai
import json

from langchain.chains import LLMChain, RetrievalQA, ConversationalRetrievalChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationTokenBufferMemory
from langchain.prompts import PromptTemplate
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI

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
        self.db, self.template = self.db.open_database()
        self.temperature = config['temperature']


    def initialize_chat(self):
        llm = ChatOpenAI(
            temperature=self.temperature,
            openai_api_key=openai.api_key,
            model_name=self.model_name,
        )

        PROMPT = PromptTemplate(
            template=self.template, input_variables=["context", "question"]
        )
        chain_type_kwargs = {"prompt": PROMPT, 'verbose': False}


        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=self.db.as_retriever(),
            chain_type_kwargs=chain_type_kwargs
        )
        return qa_chain







