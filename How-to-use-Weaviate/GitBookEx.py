import weaviate
from weaviate.classes.init import Auth
import os
from weaviate.classes.config import Configure
from weaviate.classes.config import Property
from weaviate.classes.config import DataType
import weaviate.classes as wvc
from typing import List, Optional, Any
import requests
import re

client: Optional[weaviate.WeaviateClient] = None
git_collection: Any = None

# Best practice: store your credentials in environment variables
weaviate_url = os.environ["WEAVIATE_URL"]
weaviate_api_key = os.environ["WEAVIATE_API_KEY"]
cohere_api_key = os.environ["COHERE_APIKEY"]

def connect_weaviate():
    global client
    global openai_key
    if client is None:
        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=weaviate_url,  # Replace with your Weaviate Cloud URL
            auth_credentials=Auth.api_key(weaviate_api_key), # Replace with your Weaviate Cloud key
            headers={
                "X-Cohere-Api-Key": cohere_api_key
            }
        )
        print("Client is ready: ", client.is_ready())  # Should print: `True`
        print(client._connection._headers)


def create_collection():
    global git_collection
    collection_name = "GitBookChunk"

    if client.collections.exists(collection_name):  # In case we've created this collection before
        client.collections.delete(collection_name)  # THIS WILL DELETE ALL DATA IN THE COLLECTION

    git_collection = client.collections.create(
        name=collection_name,
        properties=[
            Property(
                name="chunk",
                data_type=DataType.TEXT
            ),
            Property(
                name="chapter_title",
                data_type=DataType.TEXT
            ),
            Property(
                name="chunk_index",
                data_type=DataType.INT
            ),
        ],
        vectorizer_config=Configure.Vectorizer.text2vec_weaviate(),  # Configure the Weaviate Embeddings integration
        generative_config=Configure.Generative.cohere()  # Configure the Cohere generative AI integration
    )


def download_and_chunk(src_url: str, chunk_size: int, overlap_size: int) -> List[str]:
    response = requests.get(src_url)  # Retrieve source text
    source_text = re.sub(r"\s+", " ", response.text)  # Remove multiple whitespaces
    text_words = re.split(r"\s", source_text)  # Split text by single whitespace

    chunks = []
    for i in range(0, len(text_words), chunk_size):  # Iterate through & chunk data
        chunk = " ".join(text_words[max(i - overlap_size, 0): i + chunk_size])  # Join a set of words into a string
        chunks.append(chunk)
    return chunks


def insert_chunks_in_weaviate():
    pro_git_chapter_url = "https://raw.githubusercontent.com/progit/progit2/main/book/01-introduction/sections/what-is-git.asc"
    chunked_text = download_and_chunk(pro_git_chapter_url, 150, 25)

    #import the data into Weaviate
    chunks_list = list()
    for i, chunk in enumerate(chunked_text):
        data_properties = {
            "chapter_title": "What is Git",
            "chunk": chunk,
            "chunk_index": i
        }
        data_object = wvc.data.DataObject(properties=data_properties)
        chunks_list.append(data_object)
    git_collection.data.insert_many(chunks_list)


#running a simple aggregation query to check all data imported
def check_data_imported():
    response = git_collection.aggregate.over_all(total_count=True)
    print(response.total_count)


#RAG in weaviate
def perform_rag():
    git_collection = client.collections.get("GitBookChunk")
    response = git_collection.generate.near_text(
        query="states of git",
        limit=2,
        grouped_task="Write a trivia tweet based on this text. Use emojis and make it succinct and cute."
    )

    print("***Response generated from grouped task*** \n", response.generated, end="\n\n")


def perform_another_rag():
    git_collection = client.collections.get("GitBookChunk")
    response = git_collection.generate.near_text(
        query="how git saves data",
        limit=2,
        single_prompt="Translate this into French: {chunk}"
    )

    for obj in response.objects:
        print("***Chunk received from querying weaviate database*** \n", obj.properties["chunk"], end="\n\n")
        print("***Response generated from single prompt*** \n", obj.generated, end="\n\n")


def free_client():
    global client
    client.close()  # Free up resources


connect_weaviate()
create_collection()
insert_chunks_in_weaviate()
check_data_imported()
perform_rag()
perform_another_rag()
free_client()
