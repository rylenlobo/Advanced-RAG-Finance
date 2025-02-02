import os
from llama_index.core import Document, StorageContext, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.kdbai import KDBAIVectorStore
import kdbai_client as kdbai

# Initialize KDB.AI session
KDBAI_ENDPOINT = os.environ.get("KDBAI_ENDPOINT", "https://cloud.kdb.ai/instance/tf1iao2fou")
KDBAI_API_KEY = os.environ.get("KDBAI_API_KEY", "7c8f3aa023-S8KdVyYjqE2lMuqZf+mg2XVr9NxABOa4nQGSF5PJnA04Jf8HhJzdJfDK8hMaxM5Sllu02RX5meMQWdCk")
session = kdbai.Session(endpoint=KDBAI_ENDPOINT, api_key=KDBAI_API_KEY)

# Define schema and index for KDB.AI
schema = [
    {"name": "document_id", "type": "bytes"},
    {"name": "text", "type": "bytes"},
    {"name": "embeddings", "type": "float32s"},
    {"name": "url", "type": "str"},
    {"name": "title", "type": "str"},
    {"name": "issue_date", "type": "datetime64[ns]"},
]

indexFlat = {
    "name": "flat_index",
    "type": "flat",
    "column": "embeddings",
    "params": {"dims": 768, "metric": "L2"},
}

# Create KDB.AI table
database = session.database("default")
table = database.create_table("rag", schema=schema, indexes=[indexFlat])

# Initialize HuggingFace embedding model
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Create vector store and storage context
vector_store = KDBAIVectorStore(table, schema=schema, index=indexFlat['name'])
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Load documents and create index
documents = [Document(text="Sample text", metadata={"title": "Sample"})]
index = VectorStoreIndex.from_documents(documents, storage_context=storage_context, embed_model=embed_model)

# Query the index
query_engine = index.as_query_engine()
response = query_engine.query("What is the sample text?")
print(response)
