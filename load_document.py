from langchain_community.document_loaders import PyPDFLoader
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

file_path= "stockgenie.pdf"
if not os.path.exists(file_path):
    raise FileNotFoundError(f"The file {file_path} does not exist.")
else:
    print(f"Loading document from {file_path}")
    loader = PyPDFLoader(file_path)
    document = loader.load()

# Split the document into chunks.
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
docs = text_splitter.split_documents(document)
print(f"Number of document chunks: {len(docs)}")


# Initialize the embedding model.
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
# Create a vector store from the document chunks and embeddings.
vectorstore = Chroma.from_documents(
    documents=docs, 
    embedding=embeddings,
    persist_directory="./chroma_db"
)
# Create a retriever that will fetch relevant documents.
retriever = vectorstore.as_retriever()
print("Document loaded and processed successfully.")