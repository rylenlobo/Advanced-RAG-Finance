from flask import Flask, request, Response, jsonify
from dotenv import load_dotenv
import os

import json
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


from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.config.parser import ConfigParser


# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
os.environ["KMP_DUPLICATE_LIB_OK"] = "True"


app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ollama settings
# Initialize the LLM model
llm = Ollama(model="llama3.2:3b-instruct-q8_0",
             temperature=0,  # Fixed typo: 'temprature' -> 'temperature'
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


class DocumentProcessor:
    def __init__(self):
        nest_asyncio.apply()

    def process_document(self, file_path):
        # Converting To MD Text
        md_processor = PDFToMarkDownTextProcessor()
        md_text = md_processor.process(file_path)

        # Create document nodes
        documents = [Document(text=part.strip(), metadata={
            'file_name': file_path,
            'page_number': i
        }) for i, part in enumerate(md_text.split('------PAGE_BREAK------')) if part.strip()]

        # ---------------------------------------------------------------------------------------------

        # Parse and extract metadata
        node_parser = MarkdownNodeParser(show_progress=True)
        qna_extractor = QuestionsAnsweredExtractor(
            questions=3, llm=llm, metadata_mode=MetadataMode.EMBED)
        summary_extractor = SummaryExtractor(
            summaries=["prev", "self", "next"], llm=llm)

        extractors = [summary_extractor]

        pipeline = IngestionPipeline(
            transformations=[node_parser, *extractors])

        nodes = pipeline.run(
            nodes=documents, in_place=False, show_progress=True)

        # Generate embeddings
        for node in nodes:
            node.embedding = embed_model.get_text_embedding(
                node.get_content(metadata_mode=MetadataMode.EMBED)
            )

        # ---------------------------------------------------------------------------------------------

        # Store in Pinecone
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

        # ---------------------------------------------------------------------------------------------


@app.route('/upload', methods=['POST'])
def upload_document():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        try:
            processor = DocumentProcessor()
            processor.process_document(file_path)

            return jsonify({
                'message': 'File uploaded and processed successfully',
                'filename': filename
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid file type'}), 400


# @app.route('/query', methods=['POST'])
# def query_document():
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
#             return jsonify({'error': f'Error processing document: {str(e)}'}), 500
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
