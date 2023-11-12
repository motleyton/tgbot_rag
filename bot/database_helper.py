import os

from langchain.document_loaders import GoogleDriveLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import openai
from langchain.vectorstores import FAISS

class Database:
    def __init__(self, config: dict):
        self.folder_id = config['folder_id']

    def open_database(self):
        folder_id = self.folder_id
        loader = GoogleDriveLoader(folder_id=folder_id,
                                   credentials_path="/home/bmf/Desktop/freelance/tgbot_rag/Credentials.json",
                                   token_path='/home/bmf/Desktop/freelance/tgbot_rag/token.json')

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000, chunk_overlap=0, separators=[" ", ",", "\n"]
        )
        docs = loader.load()
        #docs = text_splitter.split_documents(docs)

        texts = []  # Список для хранения других текстов

        # Отладочный вывод для первого элемента в списке (или всех элементов)
        for page in docs:
            # Получаем метаданные документа
            metadata = page.metadata

            # Проверяем наличие слова "Промпт" в заголовке
            if 'промпт' in metadata['title'].lower():
                prompt = page.page_content
            else:
                texts.append(page)  # Добавляем в список texts, если не нашли "Промпт"


        texts = text_splitter.split_documents(texts)
        # print(texts)
        embeddings = OpenAIEmbeddings(openai_api_key=openai.api_key)
        db = FAISS.from_documents(texts, embeddings)
        db.as_retriever()
        db.save_local('faiss_index')
        #print(prompt)

        return db, prompt

# openai_config = {
#     'folder_id': "1DKKmJ68NGvy8nXQnu-ukGpNh_pdrGkRp",
#     'prompt_id': '1k_58V2a4TuvUc8VIPZyczwQMK5ktFYRp7wUmoAXOCts',
#     'api_key': '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',
# }
#
# test = Database(openai_config)
#
# print(test.open_database())

