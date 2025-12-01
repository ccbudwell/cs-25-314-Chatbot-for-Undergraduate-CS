from llama_index.core import Document, VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.readers.apify import ApifyActor
import os
import openai
import json
import re
import logging
from dotenv import load_dotenv
from llama_index.embeddings.openai import OpenAIEmbedding

# Load env vars (from keys.env if you’re using that)
load_dotenv("keys.env")

# Logging configuration (file + console)
logger = logging.getLogger("chatbot")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("chatbot.log")
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# extra logger just for validation events
validation_logger = logging.getLogger("validation")
validation_logger.setLevel(logging.INFO)
_validation_fh = logging.FileHandler("validation.log")
_validation_fh.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
validation_logger.addHandler(_validation_fh)

logger.info("Chatbot started")

# helper to check banned characters
def _has_invalid_chars(s: str, banned: str = "![]<>@'/;") -> bool:
    return any(c in s for c in banned)

def _validate_and_sanitize(user_input: str) -> str:
    if len(user_input) > 500:
        validation_logger.info("blocked: >500 chars")
        raise ValueError("Input exceeds 500 characters.")

    if _has_invalid_chars(user_input):
        validation_logger.info("blocked: invalid characters")
        raise ValueError("Input contains invalid characters.")

    return user_input.strip()

class Chatbot:
    def __init__(self, config_file: str = "config.json"):
        # env vars (support multiple names so you’re not stuck)
        OPENAI_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_APIKEY")
        APIFY_TOKEN = (
            os.getenv("APIFY_API_KEY")
            or os.getenv("APIFY_API_TOKEN")
            or os.getenv("APIFY")
        )

        # if you’re using OpenAI anywhere directly
        if OPENAI_KEY:
            openai.api_key = OPENAI_KEY

        # use a current embedding model (fallback if needed)
        try:
            embedding_model = OpenAIEmbedding(model="text-embedding-3-small")
        except Exception:
            embedding_model = OpenAIEmbedding(model="text-embedding-ada-002")

        PERSIST_DIR = "./storage_index"

        with open(config_file, "r") as f:
            config = json.load(f)
        urls = config.get("websites", []) 
        configured_urls = [url for url in urls if url.strip()]
        urls = configured_urls
    

        logger.info(f"Loaded {len(urls)} websites from config file")

        if not urls:
            logger.error("No websites found in config file")
            raise ValueError("No websites found in config file.")

        if not os.path.exists(PERSIST_DIR):
            logger.info("Creating new index and scraping websites")
            # If you don’t want live crawling, make sure storage_index exists first
            if not APIFY_TOKEN:
                raise ValueError("APIFY token not found. Set APIFY_API_KEY (or APIFY).")

            reader = ApifyActor(APIFY_TOKEN)
            documents = reader.load_data(
                actor_id="apify/website-content-crawler",
                run_input={"startUrls": [{"url": url} for url in urls]},
                dataset_mapping_function=lambda item: Document(
                    text=item.get("text"),
                    metadata={"url": item.get("url")},
                ),
            )
            logger.info(f"Total documents scraped: {len(documents)}")

            index = VectorStoreIndex.from_documents(documents, embed_model=embedding_model)
            index.storage_context.persist(persist_dir=PERSIST_DIR)
            logger.info(f"Index persisted to {PERSIST_DIR}")
        else:
            logger.info("Loading existing index from storage")
            storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
            index = load_index_from_storage(storage_context, embed_model=embedding_model)

        self.query_engine = index.as_query_engine()
        logger.info("Query engine initialized")

    def ask_response(self, question: str):
        if question.lower() == "exit":
            logger.info("User exited the chatbot")
            return "Goodbye!"

        # Validate user input first
        try:
            clean_question = _validate_and_sanitize(question)
        except ValueError as ve:
            logger.info(f"validation_block: {ve}")
            return f"{ve} (Please rephrase and try again.)"

        # Build prompt and query
        try:
            prompt = (
                "You are an assistant tasked with answering questions based on the information available. "
                "Please provide the most accurate and concise answer you can. If the answer cannot be found in the provided data, kindly inform the user that the information is not available. "
                "Always ensure your response is clear and easy to understand."
            )

            format_style = (
                "Please answer in a short, conversational tone. Your response should be clear, direct, and concise, "
                "as if you're explaining it to a friend. Avoid excessive jargon, and if the information is not available, politely inform the user of the limitations."
            )

            full_prompt = f"{prompt}\n\nQuestion: {clean_question}\n\nFormat: {format_style}"

            response = self.query_engine.query(full_prompt)
            logger.info(f"User asked (sanitized): {clean_question} | Response returned successfully")
            return response.response

        except Exception as e:
            logger.error(f"Error parsing query: {e}")
            return f"Error parsing query: {e}"