import os
import time
from dotenv import load_dotenv, find_dotenv

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore

from pinecone import Pinecone, ServerlessSpec

load_dotenv(find_dotenv())
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not PINECONE_API_KEY:
    raise ValueError("Missing PINECONE_API_KEY in .env file")

INDEX_NAME = "sbl-rag-chatbot"

print("Initializing Indexer...")

# Pinecone DB
pc = Pinecone(api_key=PINECONE_API_KEY)

existing_indexes = [i.name for i in pc.list_indexes()]

if INDEX_NAME not in existing_indexes:
    print(f"📦 Creating new index: {INDEX_NAME}...")
    pc.create_index(
        name=INDEX_NAME,
        dimension=384,  # Must match the embedding model (all-MiniLM-L6-v2 = 384)
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1" 
        )
    )
    while not pc.describe_index(INDEX_NAME).status['ready']:
        time.sleep(1)
else:
    print(f"Found existing index: {INDEX_NAME}")

# Process txt
print("Loading knowledge_base.txt...")
loader = TextLoader("../database/knowledge_base.txt", encoding="utf-8")
docs = loader.load()

print(f"   > Loaded {len(docs[0].page_content)} characters of text.")

# Split text into chunks
# chunk_size=1000: Roughly 2-3 paragraphs.
# chunk_overlap=100.
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
splits = text_splitter.split_documents(docs)

print(f"Split into {len(splits)} chunks.")

# Embed + Upload
print("Loading Embedding Model (this runs locally)...")
# Small + fast model to embed locally
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

print("Uploading vectors to Pinecone (this might take a minute)...")

docsearch = PineconeVectorStore.from_documents(
    documents=splits,
    embedding=embeddings,
    index_name=INDEX_NAME
)

print(f"\nSuccessfully uploaded {len(splits)} vectors to Pinecone index: {INDEX_NAME}")
