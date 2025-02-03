import os
from flask import Flask, request, jsonify, send_file
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
from google.generativeai import GenerativeModel
import google.generativeai as genai
from PIL import Image
import fitz  # PyMuPDF
from pathlib import Path
import base64
import asyncio
import redis
import json
import pickle

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
llm = Ollama(
    model="llama3",  # Make sure this model name matches exactly what you have in Ollama
    base_url="http://localhost:11434",  # Explicitly set the base URL
    timeout=300,  # 5 minutes timeout
    request_timeout=300.0,  # Request timeout in seconds
)

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

# Add Gemini API configuration
GOOGLE_API_KEY = "AIzaSyAkR5NoEbXxB2nkKFdo7wNfMokp523llPg"
genai.configure(api_key=GOOGLE_API_KEY)
gemini_model = GenerativeModel('gemini-1.5-flash')

# Add this after initializing Flask app
UPLOADS_DIR = 'uploads'
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Initialize Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0)
CACHE_EXPIRATION = 3600  # Cache expiration in seconds (1 hour)

async def batch_process_images(images_data):
    """Process multiple images in a single Gemini query"""
    if not images_data:
        return []
        
    images_prompt = """Analyze these images. For each image, determine if it's a table or chart and provide analysis in this format:
    
    For tables:
    - TYPE: TABLE
    - MARKDOWN: [convert table to markdown]
    - SUMMARY: [key information from table]
    
    For charts:
    - TYPE: CHART
    - CHART_TYPE: [type of chart/graph]
    - SUMMARY: [key trends, patterns and insights]
    
    Separate each image analysis with ---"""
    
    # Convert all images to PIL format
    pil_images = []
    valid_indices = []
    
    for idx, img_data in enumerate(images_data):
        try:
            pil_img = Image.open(img_data["path"])
            pil_images.append(pil_img)
            valid_indices.append(idx)
        except Exception as e:
            print(f"Failed to process image at index {idx}: {str(e)}")
            continue
    
    if not pil_images:
        return []
    
    try:
        # Make single call to Gemini
        response = gemini_model.generate_content([images_prompt, *pil_images])
        
        # Parse response
        analyses = [a.strip() for a in response.text.split("---") if a.strip()]
        results = []
        
        # Make sure we have matching number of analyses and valid images
        for analysis_idx, analysis in enumerate(analyses):
            if analysis_idx >= len(valid_indices):
                break
                
            original_idx = valid_indices[analysis_idx]
            
            result = {
                "original_data": images_data[original_idx],
                "type": "TABLE" if "TYPE: TABLE" in analysis else "CHART"
            }
            
            if result["type"] == "TABLE":
                md_start = analysis.find("MARKDOWN:")
                summary_start = analysis.find("SUMMARY:")
                
                if md_start != -1 and summary_start != -1:
                    md_section = analysis[md_start:summary_start].strip()
                    summary_section = analysis[summary_start:].strip()
                    result.update({
                        "table_in_md": md_section.replace("MARKDOWN:", "").strip(),
                        "summary": summary_section.replace("SUMMARY:", "").strip()
                    })
            else:
                summary_start = analysis.find("SUMMARY:")
                if summary_start != -1:
                    summary_section = analysis[summary_start:].strip()
                    result.update({
                        "summary": summary_section.replace("SUMMARY:", "").strip()
                    })
                    
            results.append(result)
        
        return results
        
    except Exception as e:
        print(f"Error in batch processing: {str(e)}")
        return []


@app.route("/upload/image", methods=["POST"])
async def upload_image():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Save the uploaded file temporarily
        temp_path = os.path.join(UPLOADS_DIR, f"temp_{file.filename}")
        file.save(temp_path)

        # Process single image
        image_data = [{
            "path": temp_path,
            "page_num": 1,  # Single image, so page 1
            "img_index": 0,
            "bytes": file.read()
        }]

        # Reset file pointer after reading
        file.seek(0)

        # Process image with Gemini
        image_results = await batch_process_images(image_data)
        nodes = []

        if image_results:
            result = image_results[0]
            img_data = result["original_data"]
            img_filename = f"{result['type'].lower()}_single_{file.filename}"
            saved_img_path = os.path.join(UPLOADS_DIR, img_filename)

            # Save final image
            with open(saved_img_path, "wb") as f:
                f.write(img_data["bytes"])

            # Create node based on type
            if result["type"] == "TABLE":
                node = TextNode(
                    text=f"""Table Content:\n{result['table_in_md']}\n\nTable Summary:\n{result['summary']}""",
                    metadata={
                        "type": "table",
                        "page_num": 1,
                        "file_path": img_filename,
                        "image_path": img_filename,
                        "source_type": "table_content",
                        "reference": f"/document/image/{img_filename}",
                        "table_in_md": result['table_in_md'],
                        "summary": result['summary']
                    }
                )
            else:
                node = TextNode(
                    text=f"""Chart Summary:\n{result['summary']}""",
                    metadata={
                        "type": "chart",
                        "page_num": 1,
                        "file_path": img_filename,
                        "image_path": img_filename,
                        "source_type": "chart_content",
                        "reference": f"/document/image/{img_filename}",
                        "summary": result['summary']
                    }
                )

            # Embed and store node
            node_embedding = embed_model.get_text_embedding(node.get_content(metadata_mode="all"))
            node.embedding = node_embedding
            vector_store.add([node])

            # Clean up temporary file
            os.remove(temp_path)

            return jsonify({
                "message": "Image processed successfully",
                "type": result["type"],
                "summary": result["summary"],
                "table_in_md": result["table_in_md"] if result["type"] == "TABLE" else None,
                "image_path": f"/document/image/{img_filename}"
            }), 200
        else:
            return jsonify({"error": "Failed to process image"}), 500

    except Exception as e:
        # Clean up temporary file in case of error
        if 'temp_path' in locals():
            os.remove(temp_path)
        return jsonify({"error": f"Image processing failed: {str(e)}"}), 500


def process_and_store_document(file_path):
    # Clear existing cache when new document is added
    redis_client.flushdb()
    
    doc = fitz.open(file_path)
    nodes = []
    images_to_process = []
    
    # Store the original file path
    rel_file_path = os.path.relpath(file_path, UPLOADS_DIR)
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Extract text
        text_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)
        page_text = page.get_text("text")
        text_chunks = text_parser.split_text(page_text)
        
        # Process text chunks
        for chunk_num, text_chunk in enumerate(text_chunks):
            if text_chunk.strip():  # Only process non-empty chunks
                node = TextNode(
                    text=text_chunk,
                    metadata={
                        "type": "text",
                        "page_num": page_num + 1,
                        "chunk_num": chunk_num,
                        "file_path": rel_file_path,
                        "source_type": "document_text",
                        "reference": f"/document/{rel_file_path}?page={page_num + 1}"
                    }
                )
                nodes.append(node)

        # Collect images for batch processing
        images = page.get_images(full=True)
        for img_index, img_info in enumerate(images):
            img_xref = img_info[0]
            image_bytes = doc.extract_image(img_xref)["image"]
            
            temp_img_path = f"temp_img_{page_num}_{img_index}.png"
            with open(temp_img_path, "wb") as img_file:
                img_file.write(image_bytes)
            
            images_to_process.append({
                "path": temp_img_path,
                "page_num": page_num + 1,
                "img_index": img_index,
                "bytes": image_bytes
            })

    # Batch process all images
    if images_to_process:
        image_results = asyncio.run(batch_process_images(images_to_process))
        
        for result in image_results:
            img_data = result["original_data"]
            img_filename = f"{result['type'].lower()}_{img_data['page_num']}_{img_data['img_index']}.png"
            saved_img_path = os.path.join(UPLOADS_DIR, img_filename)
            
            # Save image
            with open(saved_img_path, "wb") as f:
                f.write(img_data["bytes"])
            
            # Create node based on type
            if result["type"] == "TABLE":
                node = TextNode(
                    text=f"""Table Content:\n{result['table_in_md']}\n\nTable Summary:\n{result['summary']}""",
                    metadata={
                        "type": "table",
                        "page_num": img_data["page_num"],
                        "file_path": rel_file_path,
                        "image_path": img_filename,
                        "source_type": "table_content",
                        "reference": f"/document/image/{img_filename}",
                        "table_in_md": result['table_in_md'],
                        "summary": result['summary']
                    }
                )
            else:
                node = TextNode(
                    text=f"""Chart Summary:\n{result['summary']}""",
                    metadata={
                        "type": "chart",
                        "page_num": img_data["page_num"],
                        "file_path": rel_file_path,
                        "image_path": img_filename,
                        "source_type": "chart_content",
                        "reference": f"/document/image/{img_filename}",
                        "summary": result['summary']
                    }
                )
            nodes.append(node)
            
        # Clean up temporary files
        for img_data in images_to_process:
            os.remove(img_data["path"])

    # Embed and store nodes
    for node in nodes:
        node_embedding = embed_model.get_text_embedding(node.get_content(metadata_mode="all"))
        node.embedding = node_embedding

    vector_store.add(nodes)

# Modify the query_vector_store function to use caching
def query_vector_store(query_str):
    # Try to get cached results
    cache_key = f"query_cache:{hash(query_str)}"
    cached_result = redis_client.get(cache_key)
    
    if cached_result:
        print("Cache hit! Using cached results")
        return pickle.loads(cached_result)
    
    print("Cache miss! Performing vector search")
    # Original query logic
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
    
    # Cache the results
    redis_client.setex(
        cache_key,
        CACHE_EXPIRATION,
        pickle.dumps(retrieved_nodes)
    )
    
    return retrieved_nodes

# Route to upload document and process it
@app.route("/upload", methods=["POST"])
def upload_document():
    print("Uploading the document")
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
async def query_document():
    try:
        data = request.get_json()
        query_str = data.get("query")
        print("Query Received ", query_str)
        if not query_str:
            return jsonify({"error": "Query string is required"}), 400

        # Limit context size by taking only most relevant chunks
        retrieved_nodes = query_vector_store(query_str)[:5]  # Limit to top 5 most relevant nodes
        
        print("Retrieved Nodes: ", retrieved_nodes)
        # Separate nodes by type
        text_nodes = [n for n in retrieved_nodes if n.metadata.get("type") == "text"]
        table_nodes = [n for n in retrieved_nodes if n.metadata.get("type") == "table"]
        chart_nodes = [n for n in retrieved_nodes if n.metadata.get("type") == "chart"]
        
        print("Text Nodes: ", text_nodes)
        print("Table Nodes: ", table_nodes)
        print("Chart Nodes: ", chart_nodes)
        # Combine context with clear separation
        context_parts = []
        
        if text_nodes:
            context_parts.append("Document Text Context:")
            context_parts.append("\n".join([n.get_content() for n in text_nodes]))
        
        if table_nodes:
            context_parts.append("\nRelevant Tables:")
            context_parts.append("\n".join([n.get_content() for n in table_nodes]))
        
        if chart_nodes:
            context_parts.append("\nRelevant Charts:")
            context_parts.append("\n".join([n.get_content() for n in chart_nodes]))
        
        print("Context Parts: ", context_parts)
        context_str = "\n\n".join(context_parts)
        fmt_qa_prompt = qa_prompt.format(context_str=context_str, query_str=query_str)
        response = llm.complete(fmt_qa_prompt)

        print("Response: ", response)
        # Enhanced source information
        source_info = []
        for node in retrieved_nodes:
            source_data = {
                "type": node.metadata.get("type", "unknown"),
                "page_num": node.metadata.get("page_num"),
                "source_type": node.metadata.get("source_type"),
                "file_path": node.metadata.get("file_path"),
                "reference": node.metadata.get("reference"),
                "content": node.get_content(),
                "metadata": node.metadata
            }
            source_info.append(source_data)

        return jsonify({
            "response": str(response),
            "sources": source_info,
            "formatted_prompt": fmt_qa_prompt
        })

    except Exception as e:
        return jsonify({"error": f"Query processing failed: {str(e)}"}), 500

# Add new endpoint to get all documents
@app.route("/documents", methods=["GET"])
def get_all_documents():
    documents = []
    for file_path in Path(UPLOADS_DIR).glob('*'):
        if file_path.suffix.lower() in ['.pdf', '.png', '.jpg', '.jpeg']:
            doc_info = {
                "filename": file_path.name,
                "path": str(file_path),
                "type": "pdf" if file_path.suffix.lower() == '.pdf' else 'image'
            }
            documents.append(doc_info)
    
    return jsonify({"documents": documents}), 200

# Add new endpoint to serve documents and images
@app.route("/document/<path:file_path>", methods=["GET"])
def get_document(file_path):
    full_path = os.path.join(UPLOADS_DIR, file_path)
    if not os.path.exists(full_path):
        return jsonify({"error": "File not found"}), 404
    
    page = request.args.get('page', type=int)
    if page and file_path.lower().endswith('.pdf'):
        doc = fitz.open(full_path)
        if 1 <= page <= len(doc):
            return send_file(full_path, download_name=file_path)
    
    return send_file(full_path, download_name=file_path)

@app.route("/document/image/<path:image_path>", methods=["GET"])
def get_image(image_path):
    full_path = os.path.join(UPLOADS_DIR, image_path)
    if not os.path.exists(full_path):
        return jsonify({"error": "Image not found"}), 404
    
    return send_file(full_path, download_name=image_path)

@app.route("/query/visual", methods=["POST"])
async def query_visual_content():
    try:
        data = request.get_json()
        query_str = data.get("query")
        print("Visual Query Received:", query_str)
        
        if not query_str:
            return jsonify({"error": "Query string is required"}), 400

        # Get all nodes but filter for only tables and charts
        retrieved_nodes = query_vector_store(query_str)
        visual_nodes = [
            n for n in retrieved_nodes 
            if n.metadata.get("type") in ["table", "chart"]
        ][:5]  # Limit to top 5 most relevant visual nodes
        
        if not visual_nodes:
            return jsonify({
                "response": "No relevant visual content found for your query.",
                "sources": []
            }), 200

        # Separate nodes by type
        table_nodes = [n for n in visual_nodes if n.metadata.get("type") == "table"]
        chart_nodes = [n for n in visual_nodes if n.metadata.get("type") == "chart"]
        
        # Combine context with clear separation
        context_parts = []
        
        if table_nodes:
            context_parts.append("Relevant Tables:")
            context_parts.append("\n".join([n.get_content() for n in table_nodes]))
        
        if chart_nodes:
            context_parts.append("\nRelevant Charts:")
            context_parts.append("\n".join([n.get_content() for n in chart_nodes]))
        
        context_str = "\n\n".join(context_parts)
        fmt_qa_prompt = qa_prompt.format(context_str=context_str, query_str=query_str)
        response = llm.complete(fmt_qa_prompt)

        # Prepare source information
        source_info = []
        for node in visual_nodes:
            source_data = {
                "type": node.metadata.get("type"),
                "page_num": node.metadata.get("page_num"),
                "file_path": node.metadata.get("file_path"),
                "image_path": node.metadata.get("image_path"),
                "reference": node.metadata.get("reference"),
                "table_in_md": node.metadata.get("table_in_md") if node.metadata.get("type") == "table" else None,
                "summary": node.metadata.get("summary")
            }
            source_info.append(source_data)

        return jsonify({
            "response": str(response),
            "sources": source_info,
            "formatted_prompt": fmt_qa_prompt
        })

    except Exception as e:
        return jsonify({"error": f"Visual query processing failed: {str(e)}"}), 500

if __name__ == "__main__":
    # Ensure the 'uploads' directory exists
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=5000)
