import os
from dotenv import load_dotenv
import pinecone as pinecone_module
import openai
from pinecone import Pinecone
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone as PineconeVS

load_dotenv()

def load_documents_from_folder(folder_path):
    documents = []
    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(folder_path, file))
            documents.extend(loader.load())
    return documents

def chunk_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    return text_splitter.split_documents(documents)

def upsert_chunks_to_pinecone(chunks, namespace="default"):
    index_name = os.getenv("PINECONE_INDEX")
    embeddings = OpenAIEmbeddings()
    # Initialize Pinecone client and obtain an index object
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENV"))
    index_obj = pc.Index(index_name)

    # Ensure the pinecone module exposes an Index type for isinstance checks
    try:
        setattr(pinecone_module, "Index", index_obj.__class__)
    except Exception:
        pass

    # Compute embeddings for each chunk and upsert directly with the Pinecone client
    texts = [getattr(d, "page_content", str(d)) for d in chunks]
    metadatas = [getattr(d, "metadata", {}) for d in chunks]

    # Embeddings: embed_documents returns a list of vectors
    try:
        vectors = embeddings.embed_documents(texts)
    except openai.RateLimitError as e:
        print("OpenAI quota/rate-limit error while creating embeddings:", e)
        print("Check your OPENAI_API_KEY, billing, and quota. Aborting ingestion.")
        return
    except Exception as e:
        print("Error while creating embeddings:", e)
        raise

    # Prepare items for upsert: (id, vector, metadata)
    upsert_items = []
    for i, (vec, meta, txt) in enumerate(zip(vectors, metadatas, texts)):
        item_id = f"doc-{i}"
        meta_payload = {"text": txt}
        if isinstance(meta, dict):
            meta_payload.update(meta)
        upsert_items.append((item_id, vec, meta_payload))

    # The Pinecone Index object's upsert API may accept different parameter names; try common one
    try:
        index_obj.upsert(vectors=upsert_items, namespace=namespace)
    except TypeError:
        try:
            index_obj.upsert(items=upsert_items, namespace=namespace)
        except Exception as e:
            print("Failed to upsert to Pinecone index:", e)
            raise
    except Exception as e:
        print("Failed to upsert to Pinecone index:", e)
        raise
    else:
        print(f"Successfully upserted {len(upsert_items)} vectors to Pinecone namespace '{namespace}'.")

def run_full_ingestion(input_folder, namespace="default"):
    print("Step 1: Loading documents...")
    docs = load_documents_from_folder(input_folder)
    print(f"Loaded {len(docs)} documents.")

    print("Step 2: Splitting into chunks...")
    chunks = chunk_documents(docs)
    print(f"Created {len(chunks)} chunks.")

    print(f"Step 3: Uploading to Pinecone namespace '{namespace}'...")
    upsert_chunks_to_pinecone(chunks, namespace=namespace)
    print("✅ Ingestion complete.")