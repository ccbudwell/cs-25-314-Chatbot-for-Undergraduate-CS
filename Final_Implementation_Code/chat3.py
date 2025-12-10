from llama_index.core import Document
from llama_index.readers.apify import ApifyActor
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
import os
import openai
import json
from llama_index.embeddings.openai import OpenAIEmbedding
from dotenv import load_dotenv

class Chatbot:
    def __init__(self, config_file="config.json"):

        load_dotenv()
        API_KEY =  os.getenv("OPENAI_APIKEY")

        APIFY = os.getenv("APIFY")

        openai.api_key = API_KEY


        embedding_model = OpenAIEmbedding(model="text-embedding-ada-002")

        PERSIST_DIR = "./storage_index"

        with open(config_file, "r") as f:
            config = json.load(f)
            urls = config.get("websites", [])
 
        if not urls:
            raise ValueError("No websites found in config file.")

        if not os.path.exists(PERSIST_DIR):
            reader = ApifyActor(APIFY)
            documents = reader.load_data(
                actor_id="apify/website-content-crawler",
                run_input={
                    # "startUrls": [
                    #     {"url": "https://bulletin.vcu.edu/undergraduate/engineering/computer-science/computer-science-bs-concentration-cybersecurity/"}
                    # ]
                    "startUrls": [{"url": url} for url in urls]
                },
                dataset_mapping_function=lambda item: Document(
                    text=item.get("text"),
                    metadata={
                        "url": item.get("url"),
                    },
                ),
            )
            print("Total documents scraped: ", len(documents))

            # Create the index from documents
            index = VectorStoreIndex.from_documents(documents, embed_model = embedding_model)

            # Persist the index for later use
            index.storage_context.persist(persist_dir=PERSIST_DIR)
        else:
            # Load the existing index
            storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
            index = load_index_from_storage(storage_context, embed_model = embedding_model) 

        self.query_engine = index.as_query_engine()



    # def ask_response(self, question):  
    #     if question.lower() == "exit":
    #         return
        
    #     # Query the index
    #     response = self.query_engine.query(question)
    #     return response.response

    def ask_response(self, question):  
        if question.lower() == "exit":
            return "Goodbye!"

        try:
            # Refined standardized prompt and format
            prompt = ("You are an assistant tasked with answering questions based on the information available. "
                      "Please provide the most accurate and concise answer you can. If the answer cannot be found in the provided data, kindly inform the user that the information is not available. "
                      "Always ensure your response is clear and easy to understand.")
            
            format_style = "Please answer in a short, conversational tone. Your response should be clear, direct, and concise, as if you're explaining it to a friend. Avoid excessive jargon, and if the information is not available, politely inform the user of the limitations."

            # Construct the full prompt for the model
            full_prompt = f"{prompt}\n\nQuestion: {question}\n\nFormat: {format_style}"

            # Query the index with the full prompt
            response = self.query_engine.query(full_prompt)

            return response.response

        except Exception as e:
            return f"Error parsing query: {e}"
