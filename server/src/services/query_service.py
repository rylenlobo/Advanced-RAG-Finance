import os
from typing import Dict, Any, Optional, Tuple
from llama_index.core import PromptTemplate
from llama_index.core.chat_engine import ContextChatEngine
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone
import nest_asyncio

from src.utils.retriever import PineconeRetriever


class QueryService:
    """Service for querying documents using chat engines with user-specific memory."""

    def __init__(self, llm, embed_model, pinecone_client):
        """Initialize with necessary components."""
        nest_asyncio.apply()
        self.llm = llm
        self.embed_model = embed_model
        self.pc = pinecone_client
        # Store chat engines by user_id and document_name
        self.chat_engines = {}

        # Default QA prompt template for context-based answering
        self.qa_prompt = """\
You are a skilled financial analyst assistant specializing in advanced RAG (Retrieval-Augmented Generation).  
Your goal is to provide clear, concise answers primarily based on the provided context.  
## Response Format:
- Reply in **markdown**.
- Dont wrap the response in ```markdown ``` that represents code in md when replying in markdown or any other code just directly output the text


## Guidelines:
- **Dont wrap the response in ``` that represents code in md when replying in markdown or any other code just directly output the text
- **Prioritize Given Context:** Answer using the provided context first, ensuring relevance.  
- **Refer to Previous Conversations If Needed:** If key details are missing, check past interactions for additional information.  
- **Perform Calculations If Required:** Show only essential steps.  
- **Address Missing Information:** If the context is insufficient, ask for clarification instead of assuming.   
- **Source Disclosure Only If Asked:** Provide only the answer unless the user requests the source.  
- **Aditionally if asked for the resource or where the documents is located you provide that
-




### Use the below context to answer:  
---------------------  
{context_str}  
---------------------  

{query_str}  

### Response:  
"""

        # Query refinement prompt
        self.query_refine_prompt = PromptTemplate("""\
  Improve the given query **only if necessary** by correcting grammar or enhancing clarity.  
Ensure the refined query strictly maintains the original intent and structure.  
ONLY RESPOND WITH THE ENHANCED QUERY AND NOTHING ELSE.  

Original Query: {query}  
""")

    def get_chat_engine_key(self, user_id: str, document_name: str) -> str:
        return f"{user_id}:{document_name}"

    def get_chat_engine(self, user_id: str, document_name: str) -> Optional[ContextChatEngine]:
        # Generate a unique key for this user-document combination
        key = self.get_chat_engine_key(user_id, document_name)

        if key in self.chat_engines:
            return self.chat_engines[key]

        # Check if index exists in Pinecone
        if document_name not in self.pc.list_indexes().names():
            return None

        # Create a new chat engine for this user-document pair
        return self._create_chat_engine(user_id, document_name)

    def _create_chat_engine(self, user_id: str, document_name: str) -> ContextChatEngine:
        """Create a new chat engine for a user-document pair.

        Args:
            user_id: The unique identifier for the user
            document_name: The name of the document (without .pdf extension)

        Returns:
            A ContextChatEngine for querying the document
        """
        pinecone_index = self.pc.Index(document_name)
        vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
        retriever = PineconeRetriever(vector_store, self.embed_model)

        # Add a reranker to improve retrieval quality
        reranker = SentenceTransformerRerank(
            model="cross-encoder/ms-marco-MiniLM-L-6-v2",
            top_n=6
        )

        # Chat memory for conversation context - user specific
        memory = ChatMemoryBuffer.from_defaults(token_limit=5000)

        # Create and store the chat engine
        chat_engine = ContextChatEngine.from_defaults(
            node_postprocessors=[reranker],
            retriever=retriever,
            memory=memory,
            llm=self.llm,
            context_template=self.qa_prompt
        )

        # Store using the combined user_id:document_name key
        key = self.get_chat_engine_key(user_id, document_name)
        self.chat_engines[key] = chat_engine
        return chat_engine

    def query_document(self, user_id: str, document_name: str, query: str):
        """Query a document with the given query for a specific user.

        Args:
            user_id: The unique identifier for the user
            document_name: The name of the document (without .pdf extension)
            query: The query to run against the document

        Returns:
            A streaming response or None if the document doesn't exist
        """
        # Get or create chat engine for this user and document
        chat_engine = self.get_chat_engine(user_id, document_name)
        if not chat_engine:
            return None

        # Refine the query if needed
        refined_query = self.llm.predict(
            self.query_refine_prompt,
            query=query
        ).strip()

        # Return streaming response
        return chat_engine.chat(refined_query)
