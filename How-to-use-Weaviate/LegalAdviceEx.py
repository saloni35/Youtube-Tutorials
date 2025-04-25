import weaviate
from weaviate.classes.init import Auth
from datasets import load_dataset
import os, json
from weaviate.classes.config import Configure

client = None
legal_advise_collection = None

# Best practice: store your credentials in environment variables
weaviate_url = os.environ["WEAVIATE_URL"]
weaviate_api_key = os.environ["WEAVIATE_API_KEY"]
cohere_api_key = os.environ["COHERE_APIKEY"]


def connect_weaviate():
    global client
    if client is None:
        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=weaviate_url, # Replace with your Weaviate Cloud URL
            auth_credentials=Auth.api_key(weaviate_api_key), # Replace with your Weaviate Cloud key
        )
        print("Client is ready: ", client.is_ready())  # Should print: `True`


def create_collection():
    global legal_advise_collection
    global client
    legal_advise_collection = client.collections.create(
        name="LegalAdvice",
        vectorizer_config=Configure.Vectorizer.text2vec_weaviate(),  # Configure the Weaviate Embeddings integration
        generative_config=Configure.Generative.cohere()  # Configure the Cohere generative AI integration
    )


def load_data_collection():
    global legal_advise_collection
    global client
    # Step 1: Load Hugging Face dataset
    dataset = load_dataset("jonathanli/legal-advice-reddit", split="train[:100]")  # limit to 100 for demo
    print(dataset)

    legal_advise_collection = client.collections.get("LegalAdvice")

    with legal_advise_collection.batch.dynamic() as batch:
        for d in dataset:
            batch.add_object({
                "link": d["full_link"],
                "body": d["body"],
                "title": d["title"],
                "label": d["text_label"]
            })
            if batch.number_errors > 10:
                print("Batch import stopped due to excessive errors.")
                break

    failed_objects = legal_advise_collection.batch.failed_objects
    if failed_objects:
        print(f"Number of failed imports: {len(failed_objects)}")
        print(f"First failed object: {failed_objects[0]}")


def first_query_collection():
    legal_advise_collection = client.collections.get("LegalAdvice")

    response = legal_advise_collection.query.near_text(
        query="Provide some employment related advices",
        limit=2
    )
    for obj in response.objects:
        print("***Response received from querying weaviate database*** \n", json.dumps(obj.properties, indent=2),
              end="\n\n")

def second_query_collection():
    legal_advise_collection = client.collections.get("LegalAdvice")

    response = legal_advise_collection.query.near_text(
        query="My company is not paying my hospital bills after promising that they would. What should I do?",
        limit=2
    )
    for obj in response.objects:
        print("***Response received from querying weaviate database*** \n", json.dumps(obj.properties, indent=2),
              end="\n\n")


def free_client():
    global client
    client.close()  # Free up resources


connect_weaviate()
create_collection()
load_data_collection()
first_query_collection()
second_query_collection()
free_client()