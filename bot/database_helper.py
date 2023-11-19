from langchain.document_loaders import GoogleDriveLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import openai
from langchain.vectorstores import FAISS

import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Database:
    def __init__(self, config: dict):
        self.folder_id = config['folder_id']
        self.credentials_path = config['credentials_path']
        self.token_path = config['token_path']


    def open_database(self):
        try:
            credentials_path = self.credentials_path
            token_path = self.token_path
            loader = GoogleDriveLoader(folder_id=self.folder_id,
                                       credentials_path=credentials_path,
                                       token_path=token_path)

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=4000, chunk_overlap=0, separators=[" ", ",", "\n"]
            )

            docs = loader.load()
            docs = text_splitter.split_documents(docs)
            texts = []

            for page in docs:
                metadata = page.metadata
                if 'промпт' in metadata['title'].lower():
                    prompt = page.page_content
                else:
                    texts.append(page)

            embeddings = OpenAIEmbeddings(openai_api_key=openai.api_key)
            db = FAISS.from_documents(texts, embeddings)
            db.as_retriever()
            db.save_local('faiss_index')

            return db, prompt
        except Exception as e:
            logger.exception("Произошла ошибка при обновлении базы данных: %s", e)
            raise

