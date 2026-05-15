import os

# This line stops the [transformers] advisory warnings
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"

import chromadb
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import StorageContext, VectorStoreIndex, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

CHROMA_PATH = "./chroma_db"

def init_settings():
    """Initializes the LLM and Embedding models from your original script."""
    Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.1)
    # Using the local BGE model you used in test.py
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    Settings.node_parser = SentenceSplitter(
        chunk_size=1024,  # Larger chunks keep more context together
        chunk_overlap=200  # Overlap ensures no info is lost at the cut-off
    )

def get_chroma_index():
    """Connects to ChromaDB and returns the LlamaIndex."""
    init_settings()
    
    # Initialize the persistent Chroma client
    db = chromadb.PersistentClient(path=CHROMA_PATH)
    chroma_collection = db.get_or_create_collection("pdf_rag_collection")
    
    # Set up Chroma as the storage backend
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # Load the index (it will be empty if first run, or loaded from disk if files exist)
    return VectorStoreIndex.from_documents([], storage_context=storage_context)