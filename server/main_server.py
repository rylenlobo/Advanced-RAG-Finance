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

if __name__ == "__main__":
    # Ensure the 'uploads' directory exists
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=5000)
