from langchain.vectorstores import Pinecone
from langchain_openai import OpenAIEmbeddings
import pinecone
import os

class VectorStore:
    def __init__(self, index_name ):
        self._index_name = index_name
        self._embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    def add_vector(self, to_add):
        Pinecone.from_documents(to_add, self._embeddings, index_name=self._index_name)