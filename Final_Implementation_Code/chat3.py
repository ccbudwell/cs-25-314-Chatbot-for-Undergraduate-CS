from llama_index.core import Document
from llama_index.readers.apify import ApifyActor
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
import os
import openai
import json
from llama_index.embeddings.openai import OpenAIEmbedding
from dotenv import load_dotenv
import logging  # Added for logging
from dotenv import load_dotenv
import time
load_dotenv("keys.env")
# -----------------------------
# Logging configuration (file + console)
# -----------------------------
logger = logging.getLogger("chatbot")
logger.setLevel(logging.INFO)

# File handler
file_handler = logging.FileHandler("chatbot.log")
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# Add both handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.info("Chatbot started")

RATE_LIMIT_MAX_REQUESTS = 12 # Maximum requests allowed
RATE_LIMIT_WINDOW_SECONDS = 60 # Time window in seconds
COOLDOWN_SECONDS = 30 # Cooldown period in seconds

request_timestamps = [] # List to track timestamps of requests
blocked_until = 0.0  # Timestamp until which requests are blocked

def check_rate_limit():
    global request_timestamps, blocked_until

    current_time = time.time() # Current timestamp

    if current_time < blocked_until:
        remaining_block_time = int(blocked_until - current_time) + 1 
        logger.info(f"Rate limit exceeded. User is blocked for {remaining_block_time} more seconds.")
        raise RuntimeError(f"Rate limit exceeded. Please wait {remaining_block_time} seconds before trying again.")
    
    # Remove timestamps outside the time window so that the chat
    new_list = []
    for timestamp in request_timestamps:
        if current_time - timestamp < RATE_LIMIT_WINDOW_SECONDS:
            new_list.append(timestamp)
    
    request_timestamps = new_list

    #If we hit the limit, start the cooldown
    if len(request_timestamps) >= RATE_LIMIT_MAX_REQUESTS:
        blocked_until = current_time + COOLDOWN_SECONDS
        logger.info(f"Rate limit exceeded. User is blocked for {COOLDOWN_SECONDS} seconds.")
        raise RuntimeError(f"Rate limit exceeded. Please wait {COOLDOWN_SECONDS} seconds before trying again.")
    # Record the new request timestamp
    request_timestamps.append(current_time)


def _validate_and_sanitize(user_input: str) -> str:
    if len(user_input) > 500:
        logger.info("validation_block: Input exceeds 500 characters")
        raise ValueError("Input exceeds 500 characters. Please shorten your question.")

    if any(char in user_input for char in "![]<>@'\"/;"):
        logger.info("validation_block: Invalid characters detected in input")
        raise ValueError("Input contains invalid characters. Please remove them and try again.")

    return user_input.strip() 



class Chatbot:
    def __init__(self, config_file="config.json"):

        load_dotenv()
        API_KEY = os.getenv("OPENAI_APIKEY")
        APIFY = os.getenv("APIFY")

        openai.api_key = API_KEY
        embedding_model = OpenAIEmbedding(model="text-embedding-ada-002")
        PERSIST_DIR = "./storage_index"

        with open(config_file, "r") as f:
            config = json.load(f)
            urls = config.get("websites", [])

        logger.info(f"Loaded {len(urls)} websites from config file")

        if not urls:
            logger.error("No websites found in config file")
            raise ValueError("No websites found in config file.")

        if not os.path.exists(PERSIST_DIR):
            logger.info("Creating new index and scraping websites")
            reader = ApifyActor(APIFY)
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
        
        try:
            check_rate_limit()
        except RuntimeError as re:
            logger.info(f"rate_limit_block: {re}")
            return str(re)

        # Validate user input first
        try:
            clean_question = _validate_and_sanitize(question)
        except ValueError as ve:
            logger.info(f"validation_block: {ve}")
            return str(ve)

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
