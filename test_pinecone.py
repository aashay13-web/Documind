import os
from dotenv import load_dotenv
from pinecone import Pinecone

# 1. Load your secret keys from the .env file
load_dotenv()

# 2. Get keys from your environment
api_key = os.getenv("PINECONE_API_KEY")
index_name = os.getenv("PINECONE_INDEX")

print(f"Checking connection for index: {index_name}...")

try:
    # 3. Initialize the Pinecone client
    pc = Pinecone(api_key=api_key)
    
    # 4. Try to connect to your index
    index = pc.Index(index_name)
    
    # 5. Ask Pinecone for the index status
    stats = index.describe_index_stats()
    
    print("✅ SUCCESS!")
    print(f"Successfully connected to Pinecone.")
    print(f"Your index has {stats['total_vector_count']} documents in it.")

except Exception as e:
    print("❌ CONNECTION FAILED")
    print(f"Error details: {e}")