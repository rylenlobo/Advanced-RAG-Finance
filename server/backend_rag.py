import os
from flask import Flask, request, jsonify, send_file, Response
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from pinecone_retriver import PineconeRetriever
from llama_index.core.schema import MetadataMode
from google.generativeai import GenerativeModel
import google.generativeai as genai
from PIL import Image
import fitz  # PyMuPDF
from pathlib import Path
import redis
import json
from llama_index.core import PromptTemplate
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.config.parser import ConfigParser
from marker.output import save_output
from llama_index.core.schema import Document
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.core.chat_engine import ContextChatEngine
from llama_index.core.memory import ChatMemoryBuffer
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.core.indices.query.query_transform.base import HyDEQueryTransform
from llama_index.core.query_engine import TransformQueryEngine
from llama_index.core import VectorStoreIndex

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()
# Define the API key for Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
# index_name = "financial-annual-report-rag-1-gaurav"/

# Check if index exists, create if it does not
# if index_name not in pc.list_indexes().names():
#     pc.create_index(
#         index_name,
#         dimension=384,
#         metric="euclidean",
#         spec=ServerlessSpec(cloud="aws", region="us-east-1")
#     )


pinecone_index = pc.Index("financial-annual-report-rag-1-gaurav")
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

# Initialize embedding model
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5", model_kwargs={
    "trust_remote_code": True
})

# Initialize LLM (Language Model)
llm = Ollama(
    model="llama3",
    stream=True,
    request_timeout=3000, # Request timeout in seconds
)
# Set the LLM and embedding model in the Settings
Settings.llm = llm
Settings.embed_model = embed_model


# Query template for LLM
qa_prompt = PromptTemplate(
    """\
You are a highly skilled financial analyst assistant specializing in advanced RAG (Retrieval Augmented Generation). Your primary goal is to provide direct and concise answers to user queries based on the provided context. While you possess advanced analytical capabilities, prioritize clarity and efficiency.

### Your Capabilities:

*   **Precise Information Retrieval:** You extract specific information directly from the provided context to answer user questions accurately.
*   **Concise Calculation and Analysis:** You perform necessary calculations (growth rates, ratios, etc.) and analysis only when explicitly required by the user's query or when essential for providing a complete answer. Show your work briefly.
*   **Contextual Awareness:** You understand the context of the provided financial information and ensure your answers are relevant.
*   **Clear and Direct Communication:** You communicate your findings in a clear, concise, and professional manner, avoiding unnecessary jargon or lengthy explanations unless specifically requested.
*   **Handling Missing Information:** If data is missing, you clearly state what is unavailable.

### How to Respond to User Queries:

1.  **Understand the User's Goal:** What specific information is the user seeking?
2.  **Locate Relevant Information in the Context:** Identify the parts of the context that directly address the user's query.
3.  **Provide a Direct and Concise Answer:** Answer the question directly using information from the context.
4.  **Show Your Work Briefly (Only When Necessary):** If a calculation is required, show the steps briefly. Avoid lengthy explanations unless the user specifically asks for them.
5.  **State Missing Information:** If the required information is not in the context, state that it is unavailable.
6.  **Avoid Overthinking:** Do not speculate, make assumptions, or provide unnecessary analysis unless explicitly asked to do so. Focus on providing direct answers based on the provided information.
7. Respond naturally and conversationally, as if you were a helpful assistant. Provide the requested information directly without citing sources unless the user asks where the information came from.
8. If a question is ambiguous or requires clarification, you can say something like, "Could you please clarify what you mean by [ambiguous term]?" or "To best answer your question, could you provide more details about [specific aspect]?
9. If a question requires some level of inference but doesn't explicitly ask for an explanation, you can provide the inferred answer directly. However, if the user asks how you arrived at the answer, then provide the reasoning and cite the relevant parts of the context.

### Context:
---------------------
{context_str}
---------------------

### User Query:
{query_str}

##Response:
"""
)

# qa_prompt = f"""You're an AI model designed to analyze images and locate all tables, including those without visible borders. For each detected table, you identify rows, columns, and cells with high precision, regardless of visual separators, capturing finer details such as text style, alignment, symbols, and any other attributes within each cell. You extract all data while preserving the exact structure seen in the image, ensuring that the output table has the same number of rows and columns. The position of attributes, values, and any text or symbols within cells should match their original positions in the image and appear the same in markdown format. Column attributes are displayed accurately at the top of each column, directly above the respective values, if present. If no column attributes are found, avoid adding any default row or column headers. If a header row is present, use it to identify column names.
# You maintain the original layout and structure as closely as possible to match the source table in the image. Following extraction, you generate a detailed summary that highlights essential figures, names, or notable patterns. You also verify if the total or any value depends on the entire column (e.g., sums, averages, or derived values) and ensure that the output reflects this correctly. Present the output in markdown format, keeping both the table structure and summary concise, and ensuring that all elements retain their original positions from the image. If no table is found in the image, return 'Table not found.' You perform these tasks without asking further questions, ensuring precision and consistency.
# Also you have the option to calculate total of values of a column if necessary based on the context in the image.
# """

# Add Gemini API configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Set the Pinecone API key as an environment variable
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

genai.configure(api_key=GOOGLE_API_KEY)
gemini_model = GenerativeModel('gemini-1.5-flash')

# Add this after initializing Flask app
UPLOADS_DIR = 'uploads'
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.environ["KMP_DUPLICATE_LIB_OK"]="True"
# Initialize Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0)
CACHE_EXPIRATION = 3600  # Cache expiration in seconds (1 hour)

# Initialize Marker configuration with reduced memory usage
marker_config = {
    "output_format": "markdown",
    "use_llm": True,
    "disable_image_extraction": True,
    "paginate_output": True,
    "model_device": "cpu",
    "model_dtype": "float16",  # Use float16 instead of float32 to reduce memory usage
    "batch_size": 1,
    "max_length": 512,  # Limit sequence length
    "low_cpu_mem_usage": True,  # Enable low memory usage
}


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
                "type": "TABLE" if "TYPE: TABLE" in analysis else "CHART",
                "summary": "No summary available"  # Default summary
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
            else:  # CHART
                chart_type_start = analysis.find("CHART_TYPE:")
                summary_start = analysis.find("SUMMARY:")
                
                if summary_start != -1:
                    summary_section = analysis[summary_start:].strip()
                    result["summary"] = summary_section.replace("SUMMARY:", "").strip()
                    
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

        
        # Creating a config parser instance with specified options
        config = {
            "output_format": "markdown",  # Outputs to markdown
            "use_llm": True,  # Enables the use of Gemini to improve accuracy
            "disable_image_extraction": True,  # Doesn't extract images, produces descriptions instead when used with use_llm
            "paginate_output":True,
            "output_dir": 'output'
            #"force_ocr": True  # Force OCR processing on the entire document (takes time, can be disabled) remove if not needed
        }
        # Initializing the config parser with the config dictionary
        config_parser = ConfigParser(config)

        # Creating a PDF converter instance with the generated config, model dictionary, processors, and renderer
        converter = PdfConverter(
            config=config_parser.generate_config_dict(),
            artifact_dict=create_model_dict(),
            processor_list=config_parser.get_processors(),
            renderer=config_parser.get_renderer()
        )

        print("Converting the PDF")
        out_folder = config_parser.get_output_folder(temp_path)
        base_fname = config_parser.get_base_filename(temp_path)

        # Converting the PDF and saving the output
        rendered = converter(temp_path)  # Pass the location of the PDF
        save_output(rendered, out_folder, base_fname )

        print("Saved the output")

        md_text = rendered.markdown

        # Split the markdown text into parts using the separator
        parts = md_text.split('------PAGE_BREAK------')

        # Create a list of Document objects from the parts, including the last part
        # Each Document includes the text and metadata with the file name and page number
        documents = [Document(text=parts[i].strip(), metadata={
                      'file_name': config_parser.get_base_filename(temp_path) + ".pdf", "page_number": i}) for i in range(len(parts)) if parts[i].strip()]

        # Parse nodes using MarkdownNodeParser
        node_parser = MarkdownNodeParser()
        # nodes = node_parser.get_nodes_from_documents(documents)
        nodes = node_parser(documents)
        print("Parsed the nodes")
        # Embed and store nodes
        for node in nodes:
             # Get the text embedding for the content of the node
            node_embedding = embed_model.get_text_embedding(
                node.get_content()
            )
            # Assign the embedding to the node's embedding attribute
            node.embedding = node_embedding
        print("Stored the nodes")

        for node in nodes:
            if hasattr(node, "excluded_embed_metadata_keys") and hasattr(node, "excluded_llm_metadata_keys"):
                del node.excluded_embed_metadata_keys
                del node.excluded_llm_metadata_keys

        # Clean up temporary file
        # os.remove(temp_path)

        return jsonify({
            "message": "Image processed successfully",
            "nodes": [node.to_dict() for node in nodes]
        }), 200

    except Exception as e:
        # Clean up temporary file in case of error
        if 'temp_path' in locals():
            os.remove(temp_path)
        return jsonify({"error": f"Image processing failed: {str(e)}"}), 500


def process_and_store_document(file_path):
    try:
          
        # Creating a config parser instance with specified options
        config = {
            "output_format": "markdown",  # Outputs to markdown
            "use_llm": True,  # Enables the use of Gemini to improve accuracy
            "disable_image_extraction": True,  # Doesn't extract images, produces descriptions instead when used with use_llm
            "paginate_output":True,
            "output_dir": 'output'
            #"force_ocr": True  # Force OCR processing on the entire document (takes time, can be disabled) remove if not needed
        }
        # Initializing the config parser with the config dictionary
        config_parser = ConfigParser(config)

        # Creating a PDF converter instance with the generated config, model dictionary, processors, and renderer
        converter = PdfConverter(
            config=config_parser.generate_config_dict(),
            artifact_dict=create_model_dict(),
            processor_list=config_parser.get_processors(),
            renderer=config_parser.get_renderer()
        )

        print("Converting the PDF")
        out_folder = config_parser.get_output_folder(file_path)
        base_fname = config_parser.get_base_filename(file_path)

        # Converting the PDF and saving the output
        rendered = converter(file_path)  # Pass the location of the PDF
        save_output(rendered, out_folder, base_fname )

        print("Saved the output")

        md_text = rendered.markdown

        # Split the markdown text into parts using the separator
        parts = md_text.split('------PAGE_BREAK------')

        # Create a list of Document objects from the parts, including the last part
        # Each Document includes the text and metadata with the file name and page number
        documents = [Document(text=parts[i].strip(), metadata={
                      'file_name': config_parser.get_base_filename(file_path) + ".pdf", "page_number": i}) for i in range(len(parts)) if parts[i].strip()]

        # Parse nodes using MarkdownNodeParser
        node_parser = MarkdownNodeParser(include_metadata=True)
        # nodes = node_parser.get_nodes_from_documents(documents)
        nodes = node_parser.get_nodes_from_documents(documents)
        print("Parsed the nodes")
        # Embed and store nodes
        for node in nodes:
             # Get the text embedding for the content of the node
            node_embedding = embed_model.get_text_embedding(
                node.get_content(metadata_mode=MetadataMode.EMBED)
            )
            # Assign the embedding to the node's embedding attribute
            node.embedding = node_embedding
        print("Stored the nodes")

        for node in nodes:
            if hasattr(node, "excluded_embed_metadata_keys") and hasattr(node, "excluded_llm_metadata_keys"):
                del node.excluded_embed_metadata_keys
                del node.excluded_llm_metadata_keys
        
        #create index acc to file name
        index_name = config_parser.get_base_filename(file_path)

        if index_name not in pc.list_indexes().names():
            pc.create_index(
                index_name,
                dimension=384,
                metric="euclidean",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            pinecone_index = pc.Index(index_name)
            vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

            vector_store.add(nodes)
        # Clean up temporary file
        os.remove(file_path)

        return True
    except Exception as e:
        print(f"Error in process_and_store_document: {str(e)}")
        raise

# Modify the query_vector_store function to use caching
# def query_vector_store(query_str):
#     # Try to get cached results
#     cache_key = f"query_cache:{hash(query_str)}"
#     cached_result = redis_client.get(cache_key)
    
#     if cached_result:
#         print("Cache hit! Using cached results")
#         return pickle.loads(cached_result)
    
#     print("Cache miss! Performing vector search")
#     # Original query logic
#     query_embedding = embed_model.get_query_embedding(query_str)
#     query_mode = "default"
#     vector_store_query = VectorStoreQuery(query_embedding=query_embedding, similarity_top_k=10, mode=query_mode)
#     query_result = vector_store.query(vector_store_query)

#     # Retrieve nodes with scores
#     nodes_with_scores = []
#     for index, node in enumerate(query_result.nodes):
#         score: Optional[float] = None
#         if query_result.similarities is not None:
#             score = query_result.similarities[index]
#         nodes_with_scores.append(NodeWithScore(node=node, score=score))

#     # Use PineconeRetriever to retrieve nodes
#     retriever = PineconeRetriever(vector_store, embed_model, query_mode="default", similarity_top_k=10)
#     retrieved_nodes = retriever.retrieve(query_str)
    
#     # Cache the results
#     redis_client.setex(
#         cache_key,
#         CACHE_EXPIRATION,
#         pickle.dumps(retrieved_nodes)
#     )
    
#     return retrieved_nodes

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

# def generate_response(retrieved_nodes, query_str, qa_prompt, llm, retriever, timeout=300):
#     try:
#         context_str = "\n\n".join([r.get_content() for r in retrieved_nodes])
#         # Limit context size to prevent overloading
#         # max_context_length = 4000  # Adjust this value based on your LLM's limits
#         # if len(context_str) > max_context_length:
#         #     context_str = context_str[:max_context_length]
#         fmt_qa_prompt = qa_prompt.format(context_str=context_str, query_str=query_str)
#         chat_engine = ContextChatEngine.from_defaults(
#             retriever=retriever,
#             llm=llm,
#             memory=ChatMemoryBuffer.from_defaults(token_limit=1024),  # Add token limit
#             system_prompt="You are a helpful AI assistant that provides concise answers based on the given context.",
#             # prefix_messages=[
#             #     "According to the context provided, answer the query explicitly based on the provided content. Keep responses focused and relevant."
#             # ]
#         )

#         # Use chat instead of direct completion
#         response = chat_engine.chat(fmt_qa_prompt)
#         return str(response),fmt_qa_prompt  # No need for formatted prompt with chat engine

#     except Exception as e:
#         error_msg = f"Error generating response: {str(e)}"
#         print(error_msg)  # Log the error
#         return f"An error occurred while processing your request: {str(e)}", None

# Route to query the vector store
# @app.route("/query", methods=["POST"])
# async def query_document():
#     try:
#         data = request.get_json()
#         query_str = data.get("query")
#         print("Query Received:", query_str)
        
#         if not query_str:
#             return jsonify({"error": "Query string is required"}), 400

#         # Set a shorter timeout for retrieval
#         retriever = PineconeRetriever(
#             vector_store, 
#             embed_model, 
#             query_mode="default", 
#             similarity_top_k=5  # Reduced from 10 to 5 for faster processing
#         )
        
#         # Add timeout for retrieval
#         retrieved_nodes = await asyncio.wait_for(
#             asyncio.to_thread(retriever.retrieve, query_str),
#             timeout=60  # 60 second timeout for retrieval
#         )

#         response, fmt_qa_prompt = generate_response(
#             retrieved_nodes=retrieved_nodes,
#             query_str=query_str,
#             qa_prompt=qa_prompt,
#             llm=llm,
#             retriever=retriever,
#             timeout=120  # Reduced timeout for response generation
#         )

#         # Only include essential source information
#         source_info = [{
#             "type": node.metadata.get("type", "unknown"),
#             "page_num": node.metadata.get("page_number"),
#             "context": node.get_content(),
#             "file_path": node.metadata.get("file_name")
#         } for node in retrieved_nodes[:5]]  # Limit to top 5 sources

#         return jsonify({
#             "formatted_prompt": fmt_qa_prompt,
#             "response": str(response),
#             "sources": source_info
#         })

#     except asyncio.TimeoutError:
#         return jsonify({
#             "error": "Request timed out. Please try a more specific query or try again later."
#         }), 504
#     except Exception as e:
#         print(f"Error in query_document: {str(e)}")  # Log the error
#         return jsonify({
#             "error": f"Query processing failed: {str(e)}"
#         }), 500


# api for stream response
# @app.route("/stream-query", methods=["POST"])
# def stream_response():
#     data = request.get_json()
#     query_str = data.get("query")

#     retriever = PineconeRetriever(
#         vector_store, embed_model, query_mode="semantic_hybrid", similarity_top_k=10
#     )
#     memory = ChatMemoryBuffer.from_defaults(token_limit=1500)
#     chat_engine = ContextChatEngine.from_defaults(
#         retriever=retriever,
#         llm=llm,
#         memory=memory,
#         context_template=qa_prompt,
#         # Remove is_dummy_stream parameter
#         streaming=True  # Add streaming flag
#     )
    
#     def generate():
#         # Get streaming response
#         streaming_response = chat_engine.stream_chat(query_str)
#         for token in streaming_response.response_gen:
#             yield json.dumps({"response": token}) + "\n"

#     return Response(generate(), mimetype='application/json')

# api for stream response
@app.route("/stream-query", methods=["POST"])
def stream_response():
    data = request.get_json()
    query_str = data.get("query")

    retriever = PineconeRetriever(
        vector_store, embed_model, query_mode="semantic_hybrid", similarity_top_k=10
    )
    memory = ChatMemoryBuffer.from_defaults(token_limit=1500)
    
    # Create index from existing Pinecone vector store
    index = VectorStoreIndex.from_vector_store(
        vector_store, 
        embed_model=embed_model,
        llm=llm
    )
    
    # Create HyDE query transform
    hyde = HyDEQueryTransform(include_original=True)
    
    # Create base query engine
    base_query_engine = index.as_query_engine(
        streaming=True,
        similarity_top_k=10,
        chat_mode="context",
        chat_memory=memory,
        context_template=qa_prompt
    )
    
    # Wrap with HyDE transformation
    query_engine = TransformQueryEngine(
        base_query_engine,
        query_transform=hyde
    )

    def generate():
        streaming_response = query_engine.query(query_str)
        for token in streaming_response.response_gen:
            yield json.dumps({"response": token}) + "\n"

    return Response(generate(), mimetype='application/json')


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
