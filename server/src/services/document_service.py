import os
import time
import multiprocessing
import nest_asyncio
from llama_index.core import Document, Settings
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.core.extractors import SummaryExtractor, QuestionsAnsweredExtractor
from llama_index.core.schema import MetadataMode
from llama_index.core.ingestion import IngestionPipeline
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from src.services.pdf_service import PDFToMarkDownTextProcessor

# Dictionary to track processing tasks
processing_tasks = {}


class DocumentProcessor:
    """Service for processing documents and creating vector store indices"""

    def __init__(self, llm, embed_model, pinecone_client):
        nest_asyncio.apply()
        self.llm = llm
        self.embed_model = embed_model
        self.pc = pinecone_client

    def process_document(self, file_path, doc_id=None):
        """Process a document and store it in Pinecone"""
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
        extractors = [SummaryExtractor(summaries=["prev", "self", "next"], llm=self.llm),
                      QuestionsAnsweredExtractor(questions=3, llm=self.llm, metadata_mode=MetadataMode.EMBED)]

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

            node.embedding = self.embed_model.get_text_embedding(
                node.get_content(metadata_mode=MetadataMode.EMBED)
            )

        # Check for cancellation before Pinecone storage
        if doc_id and processing_tasks.get(doc_id, {}).get('cancelled', False):
            raise Exception("Processing cancelled by user")

        # Store in Pinecone
        print(f"Storing in Pinecone")
        index_name = os.path.splitext(os.path.basename(file_path))[0]
        if index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                str(index_name).lower(),
                dimension=768,
                metric="euclidean",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
        pinecone_index = self.pc.Index(index_name)
        vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
        vector_store.add(nodes)

        # Final cancellation check
        if doc_id and processing_tasks.get(doc_id, {}).get('cancelled', False):
            raise Exception("Processing cancelled by user")

        print(f"Document processing complete")

# Export the processing_tasks dictionary


def get_processing_tasks():
    return processing_tasks
