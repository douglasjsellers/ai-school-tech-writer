import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
class CodeBaseVector:
    def __init__(self, directory):
        self._directory = directory
        
    def vectorize(self):
        documents = self.build_documents()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        return text_splitter.split_documents(documents)

    def build_documents(self):
        documents = []
        for root, dirs, files in os.walk(self._directory):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    documents.append( Document(page_content=f"File {file_path}: {self.read_file_contents( file_path)}"))
        return documents
    def read_file_contents(self, file_path):
        with open(file_path, 'r') as f:
            return f.read()
