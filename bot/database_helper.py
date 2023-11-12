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

        texts = []

        for page in docs:
            metadata = page.metadata
            if 'промпт' in metadata['title'].lower():
                prompt = page.page_content
            else:
                texts.append(page)

        texts = text_splitter.split_documents(texts)
        embeddings = OpenAIEmbeddings(openai_api_key=openai.api_key)
        db = FAISS.from_documents(texts, embeddings)
        db.as_retriever()
        db.save_local('faiss_index')

        return db, prompt

