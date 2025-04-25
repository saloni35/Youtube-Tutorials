# Weaviate Python Examples: LegalAdviceEx & GitBookEx

This repository contains two Python examples demonstrating how to work with the [Weaviate Cloud](https://weaviate.io/) vector database using dynamic data ingestion and retrieval-augmented generation (RAG) techniques.

## Project Structure

- **LegalAdviceEx.py**  
  Demonstrates how to:
  - Connect to Weaviate Cloud
  - Create a collection
  - Load a Hugging Face dataset using dynamic batching
  - Insert data into the collection
  - Perform two example queries for semantic search

- **GitBookEx.py**  
  Demonstrates how to:
  - Connect to Weaviate Cloud
  - Create a collection
  - Download and split text data into chunks from a URL
  - Upload chunks with overlap to the vector store
  - Execute a Retrieval-Augmented Generation (RAG) workflow

## Prerequisites

Make sure you have the following installed:

- Python 3.12 or later

## Running Examples

Make sure you install all dependencies first:
```
pip install -r requirements.txt
```
Run both examples
```
python LegalAdviceEx.py
python GitBookEx.py
```
