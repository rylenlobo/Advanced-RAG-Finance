from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import datetime
import json
from supabase import create_client
from werkzeug.utils import secure_filename
from llama_index.core import Settings
# from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core import Document
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.core.extractors import SummaryExtractor, QuestionsAnsweredExtractor
from llama_index.core.schema import MetadataMode
from llama_index.core.ingestion import IngestionPipeline
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.retrievers import BaseRetriever
from llama_index.core import QueryBundle, PromptTemplate
from llama_index.core.vector_stores import VectorStoreQuery
from llama_index.core.schema import NodeWithScore
# from llama_index.core.chat_engine import ContextChatEngine
# from llama_index.core.memory import ChatMemoryBuffer
# from llama_index.core.postprocessor import SentenceTransformerRerank
from pinecone import Pinecone, ServerlessSpec
import nest_asyncio
from typing import List, Optional, Any
import multiprocessing
import signal
import sys

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.config.parser import ConfigParser
import time


# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
os.environ["KMP_DUPLICATE_LIB_OK"] = "True"

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

# Configure CORS more explicitly to handle preflight requests
CORS(app, origins=["http://localhost:3000"], supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to check if file extension is allowed


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to add CORS headers to all responses


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin',
                         'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


# ollama settings
# Initialize the LLM model
llm = Ollama(model="llama3.2:3b-instruct-q8_0",
             temprature=0,
             request_timeout=3000,)

# Initialize the embedding model
embed_model = OllamaEmbedding(
    model_name="llama3.2:3b-instruct-q8_0",
    base_url="http://localhost:11434",
    ollama_additional_kwargs={"mirostat": 0},
)

# Set the LLM and embedding model in the Settings
Settings.llm = llm
Settings.embed_model = embed_model

# Initialize Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
pc = Pinecone(api_key=PINECONE_API_KEY)


class PineconeRetriever(BaseRetriever):
    def __init__(
        self,
        vector_store: PineconeVectorStore,
        embed_model: Any,
        query_mode: str = "hybrid",
        similarity_top_k: int = 15,
    ) -> None:
        self._vector_store = vector_store
        self._embed_model = embed_model
        self._query_mode = query_mode
        self._similarity_top_k = similarity_top_k
        super().__init__()

    def retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        if query_bundle.embedding is None:
            query_embedding = self._embed_model.get_query_embedding(
                query_bundle.query_str
            )
        else:
            query_embedding = query_bundle.embedding

        vector_store_query = VectorStoreQuery(
            query_embedding=query_embedding,
            similarity_top_k=self._similarity_top_k,
            mode=self._query_mode,
        )
        query_result = self._vector_store.query(vector_store_query)

        nodes_with_scores = []
        for index, node in enumerate(query_result.nodes):
            score: Optional[float] = None
            if query_result.similarities is not None:
                score = query_result.similarities[index]
            nodes_with_scores.append(NodeWithScore(node=node, score=score))

        return nodes_with_scores


class PDFToMarkDownTextProcessor():
    def __init__(self):
        self.config = {
            "output_format": "markdown",
            "use_llm": True,
            "disable_image_extraction": True,
            "paginate_output": True,
            "output_dir": 'output',
            "use_fast": True,
            "gemini_api_key": GOOGLE_API_KEY,
        }

        self.config_parser = ConfigParser(self.config)

        self.converter = PdfConverter(
            config=self.config_parser.generate_config_dict(),
            artifact_dict=create_model_dict(),
            processor_list=self.config_parser.get_processors(),
            renderer=self.config_parser.get_renderer()
        )

    def process(self, file_path):
        rendered = self.converter(file_path)
        return rendered.markdown

    def process_with_timeout(self, file_path, result_queue, timeout=300):
        """Run the process with a timeout, allowing for interruption"""
        try:
            print(f"PDF processor: Starting conversion of {file_path}")
            result = self.process(file_path)
            print(f"PDF processor: Finished conversion, putting result in queue")
            result_queue.put(result)
        except Exception as e:
            print(f"PDF processor error: {str(e)}")
            result_queue.put(f"ERROR: {str(e)}")
        finally:
            # Ensure queue has something even if there's an unexpected error
            if result_queue.empty():
                result_queue.put("ERROR: Unknown error in PDF processing")


class DocumentProcessor:
    def __init__(self):
        nest_asyncio.apply()

    def process_document(self, file_path, doc_id=None):

        # Check for cancellation before starting
        if doc_id and processing_tasks.get(doc_id, {}).get('cancelled', False):
            raise Exception("Processing cancelled by user")

        # Converting To MD Text using a separate process that can be terminated
        print(f"Starting PDF to Markdown conversion for {file_path}")

        # Use Manager for more reliable cross-process communication
        manager = multiprocessing.Manager()
        result_queue = manager.Queue()

        # Create and start the process
        md_processor = PDFToMarkDownTextProcessor()
        process = multiprocessing.Process(
            target=md_processor.process_with_timeout,
            args=(file_path, result_queue)
        )

        # Store the process in processing_tasks to be able to terminate it
        if doc_id:
            processing_tasks[doc_id]['process'] = process

        process.start()
        print(f"Started PDF conversion process with PID: {process.pid}")

        # Wait for the process to complete or be cancelled
        process_timeout = 600  # 10 minutes max
        process_wait_interval = 1  # Check every second

        for i in range(process_timeout):
            # Check if process is done
            if not process.is_alive():
                print(f"PDF conversion process completed after {i} seconds")
                break

            # Check for cancellation
            if doc_id and processing_tasks.get(doc_id, {}).get('cancelled', False):
                print(f"Terminating PDF conversion process for {doc_id}")
                process.terminate()
                process.join(5)  # Give it 5 seconds to terminate
                if process.is_alive():
                    process.kill()  # Force kill if still alive
                raise Exception("Processing cancelled by user")

            # Wait a bit before checking again
            time.sleep(process_wait_interval)

        # If we got here and process is still running, it timed out
        if process.is_alive():
            print(f"PDF conversion timed out after {process_timeout} seconds")
            process.terminate()
            process.join(5)
            if process.is_alive():
                process.kill()
            raise Exception("PDF conversion timed out")

        # Get the result from the queue with timeout
        try:
            print("Waiting for result from PDF conversion...")
            # Wait max 10 seconds for result
            md_text = result_queue.get(block=True, timeout=10)
            print("Got result from PDF conversion queue")

            # Check if there was an error
            if isinstance(md_text, str) and md_text.startswith("ERROR:"):
                print(f"PDF conversion reported error: {md_text}")
                raise Exception(md_text)
        except Exception as e:
            if "queue empty" in str(e).lower():
                print("Queue was empty, PDF conversion failed to produce result")
                raise Exception("PDF conversion failed to produce output")
            else:
                print(f"Error getting result from queue: {str(e)}")
                raise

        # Check for cancellation after markdown conversion
        if doc_id and processing_tasks.get(doc_id, {}).get('cancelled', False):
            raise Exception("Processing cancelled by user")

        print(f"Creating document nodes")
        # Create document nodes
        # Extract just the filename without the path
        filename = os.path.basename(file_path)
        documents = [Document(text=part.strip(), metadata={
            'file_name': filename,
            'page_number': i
        }) for i, part in enumerate(md_text.split('------PAGE_BREAK------')) if part.strip()]

        # Check for cancellation after creating document nodes
        if doc_id and processing_tasks.get(doc_id, {}).get('cancelled', False):
            raise Exception("Processing cancelled by user")

        # Parse and extract metadata
        print(f"Parsing and extracting metadata")
        node_parser = MarkdownNodeParser(show_progress=True)
        extractors = [SummaryExtractor(summaries=["prev", "self", "next"], llm=llm), QuestionsAnsweredExtractor(
            questions=3, llm=llm, metadata_mode=MetadataMode.EMBED),]

        pipeline = IngestionPipeline(
            transformations=[node_parser, *extractors])

        nodes = pipeline.run(
            nodes=documents, in_place=False, show_progress=True)

        # Check for cancellation after pipeline run
        if doc_id and processing_tasks.get(doc_id, {}).get('cancelled', False):
            raise Exception("Processing cancelled by user")

        # Generate embeddings
        print(f"Generating embeddings")
        for i, node in enumerate(nodes):
            # Check for cancellation periodically during embedding generation
            if doc_id and i % 5 == 0 and processing_tasks.get(doc_id, {}).get('cancelled', False):
                raise Exception("Processing cancelled by user")

            node.embedding = embed_model.get_text_embedding(
                node.get_content(metadata_mode=MetadataMode.EMBED)
            )

        # Check for cancellation before Pinecone storage
        if doc_id and processing_tasks.get(doc_id, {}).get('cancelled', False):
            raise Exception("Processing cancelled by user")

        # Store in Pinecone
        print(f"Storing in Pinecone")
        index_name = os.path.splitext(os.path.basename(file_path))[0]
        if index_name not in pc.list_indexes().names():
            pc.create_index(
                index_name,
                dimension=3072,
                metric="euclidean",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
        pinecone_index = pc.Index(index_name)
        vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
        vector_store.add(nodes)

        # Final cancellation check
        if doc_id and processing_tasks.get(doc_id, {}).get('cancelled', False):
            raise Exception("Processing cancelled by user")

        print(f"Document processing complete")


# Track ongoing processing tasks
processing_tasks = {}


def process_doc(doc_id, file_path):
    """Function to handle document processing without blocking the upload response"""
    import threading

    def process_thread():
        try:
            # Get document from database
            response = supabase.table('documents').select(
                '*').eq('id', doc_id).execute()
            if not response.data:
                print(f"Document {doc_id} not found in database")
                return

            # Check for cancellation before starting
            if processing_tasks.get(doc_id, {}).get('cancelled', False):
                raise Exception("Processing cancelled by user")

            print(f"Starting actual document processing for {doc_id}...")

            # Use the DocumentProcessor to process the document
            processor = DocumentProcessor()

            # Check for cancellation again before processing
            if processing_tasks.get(doc_id, {}).get('cancelled', False):
                raise Exception("Processing cancelled by user")

            # Actually process the document with the doc_id for cancellation checking
            processor.process_document(file_path, doc_id)

            # Final cancellation check
            if processing_tasks.get(doc_id, {}).get('cancelled', False):
                raise Exception("Processing cancelled by user")

            print(f"Document processing completed for {doc_id}")

            # Update status to processed
            supabase.table('documents').update({
                'status': 'processed',
            }).eq('id', doc_id).execute()
            processing_tasks[doc_id]['status'] = 'processed'

        except Exception as e:
            print(f"Error processing document {doc_id}: {str(e)}")
            status = 'cancelled' if str(
                e) == "Processing cancelled by user" else 'failed'

            # Delete the document from Supabase for any error
            try:
                supabase.table('documents').delete().eq('id', doc_id).execute()
                print(f"Deleted document {doc_id} from database due to error")
            except Exception as db_error:
                print(f"Failed to delete document {doc_id}: {str(db_error)}")

            # Clean up the file
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"Deleted file {file_path}")
                except Exception as file_error:
                    print(
                        f"Failed to delete file {file_path}: {str(file_error)}")

            processing_tasks[doc_id]['status'] = status

    # Start processing in a separate thread
    thread = threading.Thread(target=process_thread)
    thread.daemon = True
    thread.start()


@app.route('/upload', methods=['POST'])
def upload_document():
    doc_id = None
    file_path = None

    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        if 'user_id' not in request.form:
            return jsonify({'error': 'No user_id provided'}), 400

        user_id = request.form['user_id']
        title = request.form.get('title', 'Untitled Document')
        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            # Create document details with processing status in Supabase
            document_data = {
                'user_id': user_id,
                'file_name': filename,
                'title': title,
                'status': 'processing',

            }

            # Insert document into Supabase
            try:
                response = supabase.table('documents').insert(
                    document_data).execute()
                if not response.data:
                    return jsonify({'error': 'Failed to create document record in database'}), 500
                doc_id = response.data[0]['id']
            except Exception as e:
                # Clean up the file if database insertion fails
                if os.path.exists(file_path):
                    os.remove(file_path)
                print(f"Supabase error: {str(e)}")
                return jsonify({'error': f'Database error: {str(e)}'}), 500

            # Store processing status for this document
            processing_tasks[doc_id] = {
                'status': 'processing', 'cancelled': False}

            # Start simulated processing automatically
            try:
                # Simulate processing in a non-blocking way (without await)
                # In a production environment, you would use a task queue or background worker here
                process_doc(doc_id, file_path)

                return jsonify({
                    'message': 'File uploaded and processing started',
                    'status': 'processing',
                    'doc_id': doc_id
                }), 202
            except Exception as e:
                # Delete from database and clean up file if processing start fails
                try:
                    if doc_id:
                        supabase.table('documents').delete().eq(
                            'id', doc_id).execute()
                except Exception as db_error:
                    print(
                        f"Failed to delete document {doc_id}: {str(db_error)}")

                if os.path.exists(file_path):
                    os.remove(file_path)

                print(f"Processing error: {str(e)}")
                return jsonify({'error': f'Failed to start processing: {str(e)}'}), 500

        return jsonify({'error': 'Invalid file type'}), 400

    except Exception as e:
        # Clean up on any other error
        try:
            if doc_id:
                supabase.table('documents').delete().eq('id', doc_id).execute()
        except Exception as db_error:
            print(f"Failed to delete document: {str(db_error)}")

        if file_path and os.path.exists(file_path):
            os.remove(file_path)

        print(f"Unexpected error in upload: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/cancel-processing/<doc_id>', methods=['POST'])
def cancel_processing(doc_id):
    try:
        # Check if document exists in database
        response = supabase.table('documents').select(
            '*').eq('id', doc_id).execute()
        if not response.data:
            return jsonify({'error': 'Document not found'}), 404

        # Get the document info
        document = response.data[0]
        file_path = os.path.join(UPLOAD_FOLDER, document['file_name'])

        # Mark as cancelled in processing_tasks if it exists
        if doc_id in processing_tasks:
            processing_tasks[doc_id]['cancelled'] = True
            processing_tasks[doc_id]['status'] = 'cancelled'

            # Terminate any running process
            if 'process' in processing_tasks[doc_id] and processing_tasks[doc_id]['process']:
                process = processing_tasks[doc_id]['process']
                if process.is_alive():
                    print(f"Terminating process for {doc_id}")
                    process.terminate()
                    process.join(5)  # Give it 5 seconds to terminate
                    if process.is_alive():
                        process.kill()  # Force kill if still alive

        # Delete the document from Supabase
        supabase.table('documents').delete().eq('id', doc_id).execute()

        # Clean up the file
        if os.path.exists(file_path):
            os.remove(file_path)

        return jsonify({
            'message': 'The upload was cancelled',
            'status': 'cancelled'
        }), 200

    except Exception as e:
        print(f"Error in cancel-processing: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


if __name__ == '__main__':
    # For multiprocessing to work properly on Windows
    multiprocessing.freeze_support()
    # Configure logging to see process outputs clearly
    import logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    app.run(host='0.0.0.0', port=5000)


# @app.route('/query', methods=['POST'])
# # def query_document():
#     data = request.json
#     if not data or 'query' not in data or 'filename' not in data:
#         return jsonify({'error': 'Missing query or filename'}), 400

#     filename = data['filename']
#     query = data['query']
#     base_fname = os.path.splitext(filename)[0]

#     processor = DocumentProcessor()
#     if base_fname not in processor.chat_engines:
#         try:
#             file_path = os.path.join(UPLOAD_FOLDER, filename)
#             chat_engine = processor.process_document(file_path)
#         except Exception as e:
#             return jsonify({'error': f'Error processing document: {str(e)}')}), 500
#     else:
#         chat_engine = processor.chat_engines[base_fname]

#     try:
#         # Query refinement
#         query_refine_prompt = PromptTemplate(
#             """... your query refinement prompt ...""")
#         refined_query = llm.predict(query_refine_prompt, query=query).strip()

#         # Get response#     data = request.json
#         response = chat_engine.stream_chat(refined_query)ery' not in data or 'filename' not in data:
#         return Response(me'}), 400
#             (token for token in response.response_gen),
#             mimetype='text/event-stream'
#         )
#     except Exception as e:fname = os.path.splitext(filename)[0]
#         return jsonify({'error': str(e)}), 500
#         try:
#             file_path = os.path.join(UPLOAD_FOLDER, filename)
#             chat_engine = processor.process_document(file_path)
#         except Exception as e:
#             return jsonify({'error': f'Error processing document: {str(e)}')}), 500
#     else:
#         chat_engine = processor.chat_engines[base_fname]

#     try:
#         # Query refinement
#         query_refine_prompt = PromptTemplate(
#             """... your query refinement prompt ...""")
#         refined_query = llm.predict(query_refine_prompt, query=query).strip()

#         # Get response
#         response = chat_engine.stream_chat(refined_query)
#         return Response(
#             (token for token in response.response_gen),
#             mimetype='text/event-stream'
#         )
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
