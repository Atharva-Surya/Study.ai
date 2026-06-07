import os
import glob
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Use absolute path based on this script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(SCRIPT_DIR, "data")
os.makedirs(data_dir, exist_ok=True)
pdf_files = glob.glob(os.path.join(data_dir, "*.pdf"))

if not pdf_files:
    raise SystemExit(f"No PDF files found in {data_dir}/")

PDF_PATH = max(pdf_files, key=os.path.getmtime)
print(f"Ingesting PDF: {PDF_PATH}")
print("Loading PDF...")

loader = PyPDFLoader(PDF_PATH)
documents = loader.load()

print(f"Loaded {len(documents)} pages")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,
    chunk_overlap=100
)

chunks = splitter.split_documents(documents)

print(f"Created {len(chunks)} chunks")

print("Loading embedding model...")

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5"
)

print("Creating vector database...")

vectordb = FAISS.from_documents(
    chunks,
    embeddings
)

# Save to the same directory as this script
index_dir = os.path.join(SCRIPT_DIR, "faiss_index")
vectordb.save_local(index_dir)

print(f"Vector DB saved to {index_dir}")
print("Vector DB saved successfully")