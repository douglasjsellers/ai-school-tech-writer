from langchain.vectorstores import Pinecone
from langchain_openai import OpenAIEmbeddings

class VectorStore:
    def __init__(self, index_name ):
        self._index_name = index_name
        self._embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    def add_vector(self, to_add):
        Pinecone.from_documents(to_add, self._embeddings, index_name=self._index_name)

    def fetch_context(self, prompt):
        document_vectorstore = Pinecone.from_existing_index( index_name=self._index_name, embedding=self._embeddings)
        retriever = document_vectorstore.as_retriever()
        return retriever.get_relevant_documents(prompt)