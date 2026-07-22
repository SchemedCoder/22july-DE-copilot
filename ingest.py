import os
import glob
from qdrant_client import QdrantClient
from dotenv import load_dotenv

load_dotenv()

# Initialize Qdrant local file-store
qdrant_path = os.getenv("QDRANT_PATH", "./qdrant_db")
client = QdrantClient(path=qdrant_path)

# Set the embedding model (downloads and runs locally via fastembed)
client.set_model("BAAI/bge-small-en-v1.5")

COLLECTION_NAME = "de_knowledge"

def ingest_data():
    print("Starting data ingestion...")
    
    # Recreate collection to ensure a clean state
    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)
        
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=client.get_fastembed_vector_params(),
    )
    
    documents = []
    metadata = []
    ids = []
    
    # Read all files in data_sources recursively
    file_id = 0
    data_dir = os.path.join(os.path.dirname(__file__), 'data_sources')
    
    for filepath in glob.glob(os.path.join(data_dir, '**', '*.*'), recursive=True):
        if not os.path.isfile(filepath):
            continue
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        filename = os.path.basename(filepath)
        category = os.path.basename(os.path.dirname(filepath))
        
        # For this utility, we treat the whole file as a single chunk since they are small.
        # In production, you would chunk large texts using LangChain/LlamaIndex chunkers.
        documents.append(content)
        metadata.append({
            "source": filename,
            "category": category,
            "filepath": filepath
        })
        ids.append(file_id)
        file_id += 1
        
        print(f"Read {filename} ({category})")
        
    if documents:
        print(f"Adding {len(documents)} documents to Qdrant...")
        client.add(
            collection_name=COLLECTION_NAME,
            documents=documents,
            metadata=metadata,
            ids=ids
        )
        print("Ingestion complete!")
    else:
        print("No documents found in data_sources/")

if __name__ == "__main__":
    ingest_data()
