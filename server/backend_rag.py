import os
from flask import Flask, request, jsonify
import pymupdf
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import TextNode
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.vector_stores import VectorStoreQuery
from llama_index.core.response.notebook_utils import display_source_node
from pinecone_retriver import PineconeRetriever
from llama_index.core.schema import NodeWithScore
from typing import Optional

app = Flask(__name__)

# Define the API key for Pinecone
PINECONE_API_KEY = "0aa2686e-8e56-4f53-8aff-598bbfaa3570"
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "financial-annual-report-rag-1"

# Check if index exists, create if it does not
if index_name not in pc.list_indexes().names():
    pc.create_index(
        index_name,
        dimension=384,
        metric="euclidean",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

pinecone_index = pc.Index(index_name)
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

# Initialize embedding model
embed_model = HuggingFaceEmbedding()

# Initialize LLM (Language Model)
llm = Ollama(model="llama3", timeout=3000)

# Query template for LLM
qa_prompt = """\
Context information is below.
---------------------
{context_str}
---------------------
Given the context information and not prior knowledge, answer the query with it starting from the question. 

Query: {query_str}
Answer: \
"""

# Step 1: Helper function to process and store document
def process_and_store_document(file_path):
    # Step 1: Load the PDF file
    doc = pymupdf.open(file_path)

    # Step 2: Extract text from the PDF
    text_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)
    text_chunks = []
    doc_idxs = []
    
    for doc_idx, page in enumerate(doc):
        page_text = page.get_text("text")
        cur_text_chunks = text_parser.split_text(page_text)
        text_chunks.extend(cur_text_chunks)
        doc_idxs.extend([doc_idx] * len(cur_text_chunks))

    nodes = []
    for idx, text_chunk in enumerate(text_chunks):
        node = TextNode(text=text_chunk)
        src_doc_idx = doc_idxs[idx]
        nodes.append(node)

    # Step 3: Embed text and store in Pinecone
    for node in nodes:
        node_embedding = embed_model.get_text_embedding(node.get_content(metadata_mode="all"))
        node.embedding = node_embedding

    vector_store.add(nodes)

# Step 2: Helper function for querying the vector store
def query_vector_store(query_str):
    query_embedding = embed_model.get_query_embedding(query_str)
    query_mode = "default"
    vector_store_query = VectorStoreQuery(query_embedding=query_embedding, similarity_top_k=10, mode=query_mode)
    query_result = vector_store.query(vector_store_query)

    # Retrieve nodes with scores
    nodes_with_scores = []
    for index, node in enumerate(query_result.nodes):
        score: Optional[float] = None
        if query_result.similarities is not None:
            score = query_result.similarities[index]
        nodes_with_scores.append(NodeWithScore(node=node, score=score))

    # Use PineconeRetriever to retrieve nodes
    retriever = PineconeRetriever(vector_store, embed_model, query_mode="default", similarity_top_k=10)
    retrieved_nodes = retriever.retrieve(query_str)

    return retrieved_nodes

# Route to upload document and process it
@app.route("/upload", methods=["POST"])
def upload_document():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the uploaded file temporarily
    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)

    # Process the uploaded document
    process_and_store_document(file_path)

    return jsonify({"message": "Document uploaded and processed successfully!"}), 200

# Route to query the vector store
@app.route("/query", methods=["POST"])
def query_document():
    data = request.get_json()
    query_str = data.get("query")
    
    if not query_str:
        return jsonify({"error": "Query string is required"}), 400

    # Query the vector store
    retrieved_nodes = query_vector_store(query_str)

    # Generate response using LLM
    context_str = "\n\n".join([r.get_content() for r in retrieved_nodes])
    fmt_qa_prompt = qa_prompt.format(context_str=context_str, query_str=query_str)
    response = llm.complete(fmt_qa_prompt)

    return jsonify({
        "response": str(response),
        "formatted_prompt": fmt_qa_prompt
    })

if __name__ == "__main__":
    # Ensure the 'uploads' directory exists
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=5000)
