from llama_index.core.response.notebook_utils import display_source_node
from typing import Any, List
from llama_index.core.retrievers import BaseRetriever
from llama_index.core import QueryBundle
from llama_index.core.vector_stores import VectorStoreQuery
from llama_index.core.schema import NodeWithScore, MetadataMode
from typing import Optional
from llama_index.postprocessor.rankllm_rerank import RankLLMRerank
from llama_index.llms.ollama import Ollama
from llama_index.core import QueryBundle
import torch
from llama_index.core.postprocessor import LLMRerank
from llama_index.vector_stores.pinecone.base import PineconeVectorStore
# from llama_index.postprocessor.rankllm_rerank import LLMRerank


class PineconeRetriever(BaseRetriever):
    """Retriever over a pinecone vector store."""

    def __init__(
        self,
        vector_store: PineconeVectorStore,
        embed_model: Any,
        query_mode: str = "semantic_hybrid",
        similarity_top_k: int = 2,
    ) -> None:
        """Init params."""
        self._vector_store = vector_store
        self._embed_model = embed_model
        self._query_mode = query_mode
        self._similarity_top_k = similarity_top_k
        super().__init__()

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """Retrieve."""
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

        intelligent_rereanking =  LLMRerank(
            choice_batch_size=5,
            llm=Ollama(model="llama3.2:3b",context_window=10000,request_timeout=3000),
            top_n=3,
        )

        # reranker_rerankLLM = RankLLMRerank(
        #     model="rank_zephyr", top_n=3,window_size=False
        # )
        # retrieved_nodes = reranker_rerankLLM.postprocess_nodes(
        #    nodes_with_scores, query_bundle
        # )

        # del reranker_rerankLLM
        # torch.cuda.empty_cache()

       
        nodes = intelligent_rereanking.postprocess_nodes(nodes_with_scores,query_bundle)

        return nodes

