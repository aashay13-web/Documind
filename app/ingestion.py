import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore


load_dotenv()

def run_full_ingestion(directory_path: str, namespace: str = "sop"):
    print(f"📄 Loading PDFs from directory: {directory_path}")
    
    loader = PyPDFDirectoryLoader(directory_path)
    documents = loader.load()
    
    print("✂️ Splitting text into manageable chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    print(f"✅ Created {len(chunks)} chunks.")
    
    
    print("🧠 Connecting to FREE Google AI for Embeddings...")
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        output_dimensionality=768
    )
    
    index_name = os.getenv("PINECONE_INDEX")
    print(f"☁️ Uploading chunks to Pinecone index '{index_name}' in namespace '{namespace}'...")
    
    PineconeVectorStore.from_documents(
        chunks, 
        embeddings, 
        index_name=index_name,
        namespace=namespace
    )
    
    print("🎉 INGESTION COMPLETE! Your PDFs are officially in the database.")