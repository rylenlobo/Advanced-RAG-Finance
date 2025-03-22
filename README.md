# Advanced RAG for Financial Information

**Enhancing financial data analysis through Retrieval-Augmented Generation (RAG) techniques.**

## Demo Video

_For a visual demonstration of the project's capabilities, please watch the following video:_
https://github.com/user-attachments/assets/b37de4e2-3621-483f-8950-be997356cec3

## Project Overview

This project implements an advanced Retrieval-Augmented Generation (RAG) system tailored for financial information analysis. By integrating state-of-the-art tools and methodologies, the system efficiently processes complex financial documents, enabling accurate and insightful data retrieval and analysis.

## Key Features

- **Efficient Document Parsing**: Converts PDFs into Markdown using Marker for structured processing.
- **Structured Data Representation**: Uses LlamaIndex's Markdown Node Parser to segment documents into hierarchical nodes with metadata.
- **Summarization**: Generates concise summaries for each node using the SummaryExtractor from LlamaIndex.
- **Semantic Embedding**: Transforms nodes into vector embeddings using HuggingFace's `hkunlp/instructor-large` model.
- **Vector Storage**: Stores embeddings in Pinecone for fast and scalable retrieval.
- **Query Enhancement**: Corrects grammatical errors and inconsistencies in user queries to improve search accuracy.
- **Reranking Mechanism**: Utilizes the `cross-encoder/ms-marco-MiniLM-L-6-v2` model to rank retrieved results by relevance.
- **Contextual Chat Engine**: Integrates LlamaIndex's chat engine to maintain conversational context.

## System Architecture

1. **PDF Conversion**: Marker converts financial PDFs into Markdown.
2. **Node Parsing**: LlamaIndex's Markdown Node Parser segments the Markdown into structured nodes.
3. **Summarization**: SummaryExtractor generates summaries for each node.
4. **Embedding**: Nodes are embedded using HuggingFace's `hkunlp/instructor-large` model.
5. **Storage**: Embeddings are stored in Pinecone for efficient retrieval.
6. **Query Processing**: Queries undergo enhancement for better accuracy.
7. **Retrieval and Reranking**: Relevant documents are retrieved and reranked using the cross-encoder model.
8. **Conversational Interaction**: LlamaIndex's chat engine maintains contextual awareness.

## Acknowledgements

Special thanks to the developers of:
- [Marker](https://github.com/VikParuchuri/marker)
- [LlamaIndex](https://github.com/jerryjliu/llama_index)
- [HuggingFace Transformers](https://github.com/huggingface/transformers)
- [Pinecone](https://www.pinecone.io)

