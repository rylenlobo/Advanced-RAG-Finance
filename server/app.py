from flask import Flask, request, Response, jsonify, session
from flask_cors import CORS
from supabase import create_client
from werkzeug.utils import secure_filename
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from pinecone import Pinecone
import os
import threading
import multiprocessing
import logging
from dotenv import load_dotenv
import uuid

# Import from our modules
from src.config import (
    SUPABASE_URL, SUPABASE_KEY, PINECONE_API_KEY,
    UPLOAD_FOLDER, CORS_ORIGINS, HOST, PORT, allowed_file
)
from src.services.document_service import DocumentProcessor, get_processing_tasks
from src.services.query_service import QueryService
from src.utils.retriever import PineconeRetriever

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
os.environ["KMP_DUPLICATE_LIB_OK"] = "True"

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv(
    'FLASK_SECRET_KEY', 'default_secret_key_for_development')

# Configure CORS
CORS(app, origins=CORS_ORIGINS, supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
pc = Pinecone(api_key=PINECONE_API_KEY)

# Initialize LLM and embedding model
llm = Ollama(
    model="llama3.2:3b-instruct-q8_0",
    temprature=0,
    request_timeout=3000,
)

query_llm = Gemini(
    model="models/gemini-2.0-flash",
    api_key=GOOGLE_API_KEY)

embed_model = HuggingFaceEmbedding(
    model_name="hkunlp/instructor-large"
)

# Set the LLM and embedding model in the Settings
Settings.llm = llm
Settings.embed_model = embed_model

# Initialize query service
query_service = QueryService(query_llm, embed_model, pc)

# Access the processing_tasks dictionary
processing_tasks = get_processing_tasks()

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


def process_doc(doc_id, file_path):
    """Function to handle document processing without blocking the upload response"""
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

            print(f"Starting document processing for {doc_id}...")

            # Initialize and use the DocumentProcessor
            processor = DocumentProcessor(llm, embed_model, pc)

            # Process the document with the doc_id for cancellation checking
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
                'id': str(uuid.uuid4()),
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

            # Start processing
            try:
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


@app.route('/query', methods=['POST'])
def query_document():
    data = request.json
    print(data)
    if not data or 'query' not in data or 'file_name' not in data or 'conversation_id' not in data:
        return jsonify({'error': 'Missing query, file_name, or conversation_id'}), 400

    filename = data['file_name']
    query = data['query']
    query_id = data['query_id']
    conversation_id = str(data['conversation_id'])
    base_fname = os.path.splitext(filename)[0]
    document_id = str(data['document_id'])

    # Get user ID from request, session, or create a new one
    user_id = None

    # Try to get user_id from request data first
    if 'user_id' in data:
        user_id = data['user_id']

    try:
        # Check if conversation exists
        response = supabase.table('conversations').select(
            '*').eq('id', conversation_id).execute()
        if not response.data:
            # Create a new conversation if it doesn't exist
            conversation_data = {
                'id': conversation_id,
                'user_id': user_id,
                'document_id': document_id,
                'name': 'New Chat'
            }
            supabase.table('conversations').insert(conversation_data).execute()

        # Store the user query in the messages table
        user_message_data = {
            'id': query_id,
            'conversation_id': conversation_id,
            'role': 'user',
            'content': query
        }
        supabase.table('messages').insert(user_message_data).execute()

        # Query the document using the user-specific service
        response = query_service.query_document(user_id, base_fname, query)

        # Handle case where document doesn't exist
        if response is None:
            return jsonify({
                'error': f'Document {filename} not found',
                'user_id': user_id  # Return user_id for client-side storage if needed
            }), 404

        # Store the assistant's response in the messages table
        assistant_message_data = {
            'id': str(uuid.uuid4()),
            'conversation_id': conversation_id,
            'role': 'assistant',
            'content': response.response
        }
        supabase.table('messages').insert(assistant_message_data).execute()

        # Return the response
        return jsonify(assistant_message_data), 200
    except Exception as e:
        return jsonify({
            'error': str(e),
            'user_id': user_id  # Return user_id for client-side storage if needed
        }), 500


if __name__ == '__main__':
    # For multiprocessing to work properly on Windows
    multiprocessing.freeze_support()

    # Configure logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    # Start the Flask server
    app.run(host=HOST, port=PORT)
