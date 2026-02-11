import os
import time
from dotenv import load_dotenv, find_dotenv

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore

from pinecone import Pinecone, ServerlessSpec

# Load env
load_dotenv(find_dotenv())
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not PINECONE_API_KEY:
    raise ValueError("Missing PINECONE_API_KEY in .env file")

INDEX_NAME = "sbl-rag-chatbot"

print("Initializing Indexer...")

# Pinecone DB
pc = Pinecone(api_key=PINECONE_API_KEY)

existing_indexes = [i.name for i in pc.list_indexes()]

# Delete old index
if INDEX_NAME in existing_indexes:
    print(f"  Deleting existing index '{INDEX_NAME}' to ensure clean slate...")
    pc.delete_index(INDEX_NAME)
    while INDEX_NAME in [i.name for i in pc.list_indexes()]:
        time.sleep(1)
    print("Old index deleted.")

print(f"Creating new index: {INDEX_NAME} (Dimension: 384)...")
pc.create_index(
    name=INDEX_NAME,
    dimension=384,  
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1" 
    )
)
while not pc.describe_index(INDEX_NAME).status['ready']:
    time.sleep(1)

current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "../database/knowledge_base.txt")
file_path = os.path.normpath(file_path)

print(f"Loading knowledge_base.txt from: {file_path}")

try:
    loader = TextLoader(file_path, encoding="utf-8")
    docs = loader.load()
except FileNotFoundError:
    print(f"Error: Could not find file at: {file_path}")
    exit(1)

print(f"Loaded {len(docs[0].page_content)} characters of text.")

# Split text
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
splits = text_splitter.split_documents(docs)

print(f"Split into {len(splits)} chunks.")

# Embed + Upload
print("Loading Embedding Model...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

print("Uploading vectors to Pinecone...")

docsearch = PineconeVectorStore.from_documents(
    documents=splits,
    embedding=embeddings,
    index_name=INDEX_NAME
)

print(f"\n Uploaded {len(splits)} vectors to index: {INDEX_NAME}")