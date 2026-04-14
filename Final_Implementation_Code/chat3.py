from llama_index.core import Document
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.embeddings.openai import OpenAIEmbedding

from bs4 import BeautifulSoup
import pandas as pd
import requests

import json
import openai
from dotenv import load_dotenv
import os

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys.env")
load_dotenv(env_path)

# Optional debug
print("DEBUG KEY:", os.getenv("OPENAI_API_KEY"))

class Chatbot:

    def __init__(self, config_file="config.json"):

        #Get API key from environment variable
        API_KEY = os.getenv("OPENAI_API_KEY")
        openai.api_key = API_KEY

        #Choose what embedding model to use 
        embedding_model = OpenAIEmbedding(model="text-embedding-3-large")
        
        #Set the directory where the index will be stored and whether to force a rebuild of the index on each run
        PERSIST_DIR = "./storage_index"

        # If true, the index will be rebuilt from scratch on each run, ignoring any existing index stored in the specified directory.
        FORCE_REBUILD = True

        #Open and read the config file to get the list of URLs to scrape
        with open(config_file, "r") as f:
            config = json.load(f)

        #Get the list of URLs from the config file
        urls = config.get("websites", [])

        #If no URLs are found in the config file, raise an error
        if not urls:
            raise ValueError("No websites found in config file.")

        #Check if the persistent directory exists or if a rebuild is forced
        if (not os.path.exists(PERSIST_DIR)) or FORCE_REBUILD:

            #Keep track of how many URLs are discovered 
            print("URLs discovered:", len(urls))

            #Create a list to hold the documents that will be created from the scraped data
            documents = []

            #Loop through each URL and scrape the page, extract tables, and convert them to text before creating a Document object for each page
            for url in urls:
                try:

                    page_data = self.scrape_page(url)

                    text = page_data["text"]
                    tables = page_data["tables"]
                    images = page_data["images"]

                    table_text = self.tables_to_text(tables)

                    combined_content = f"""
Source URL: {url}

Page Text:
{text}

Tables (converted to text): 
{table_text}

Images on Page:
{', '.join(images)} 
"""
                    
                    documents.append(
                        Document(
                            text=combined_content,
                            metadata={"url": url}
                        )
                    )
                #Handle any exceptions that occur during scraping
                except Exception as e:
                    print("Error scraping", url, e)
            #After processing all URLs, print the total number of documents created for indexing
            print("Total documents created:", len(documents))

            #Build the vector index from the created documents using the specified embedding model and persist it to disk for future use
            index = VectorStoreIndex.from_documents(
                documents,
                embed_model=embedding_model
            )

            index.storage_context.persist(persist_dir=PERSIST_DIR)

        else:
            
            #Load the existing index from storage if it already exists 
            storage_context = StorageContext.from_defaults(
                persist_dir=PERSIST_DIR
            )

            index = load_index_from_storage(
                storage_context,
                embed_model=embedding_model
            )
        #Create a query engine from the index that will be used to answer user questions based on the indexed data
        self.query_engine = index.as_query_engine()


    # -----------------------------
    # PAGE SCRAPER (REQUESTS)
    # -----------------------------

    def scrape_page(self, url):
        #Send a response to retrieve the HTML content of the page at the specified URL with a timeout of 20 seconds. 
        response = requests.get(url, timeout=20)
        #Raise an error if the page could not be retrieved successfully (i.e., if the status code is not 200 OK). 
        if response.status_code != 200:
            raise Exception(f"Failed to fetch page: {url}")
        
        #Store the HTML content of the page in a variable for further processing. 
        html = response.text

        #Use BeatifulSoup for easier content extraction
        soup = BeautifulSoup(html, "html.parser")

        # Remove unnecessary elements
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.extract()

        #Extract the visible text from the page, using a space as a separator between elements and stripping leading/trailing whitespace.
        text = soup.get_text(separator=" ", strip=True)
        #Extract tables from the page using the extract_tables method
        tables = self.extract_tables(url)

        #Collect the URLs of all images on the page by finding all <img> tags and extracting their "src" attributes, 
        #ensuring that only valid sources are included in the list.
        images = [
            img["src"]
            for img in soup.find_all("img")
            if img.get("src")
        ]
        #Return a dictionary containing the extracted text, tables, and image URLs from the page for further processing and indexing.
        return {
            "text": text,
            "tables": tables,
            "images": images
        }


    # -----------------------------
    # TABLE EXTRACTION
    # -----------------------------

    def extract_tables(self, url):
        # Use pandas to read any HTML tables present at the specified URL and return them as a list of DataFrame objects. 
        # If an error occurs during this process (if the page does not contain any tables or if there is an issue with the URL), 
        # an empty list is returned instead.
        try:
            tables = pd.read_html(url)
            return tables
        except:
            return []


    # -----------------------------
    # TABLE → NATURAL LANGUAGE
    # -----------------------------

    def tables_to_text(self, tables):
        #Start with an empty string to accumulate the natural language descriptions of the tables.
        output = ""

        #Loop through each table in the list of tables and attempt to convert its contents into a natural language summary.
        for table in tables:

            try:
                
                output += "\nTable Summary:\n"

                # For each column in the table, extract the column name and all values from that column
                # and format this information into a readable summary that describes the contents of the table in natural language. ###
                for col in table.columns:
                    values = table[col].astype(str).tolist()

                    output += f"{col} includes values such as {', '.join(values)}. "

                output += "\n"
                
            #Skip any table that causes an error during processing and continue to the next table without 
            #interrupting the overall flow of the program.
            except:
                pass
        #Return the accumulated natural language descriptions of all the tables as a single string that 
        #can be included in the chatbot's responses to user queries.
        return output


    # -----------------------------
    # CHAT QUERY FUNCTION
    # -----------------------------

    def ask_response(self, question):
        #If the user inputs "exit" (case-insensitive), return a goodbye message and end the conversation.
        if question.lower() == "exit":
            return "Goodbye!"

        try:
            # Construct a detailed prompt for the language model that instructs it to answer questions based solely on the information available
            # in the indexed documents, with a specific focus on official VCU sources and strict rules for interpreting course information. 
            # The prompt emphasizes accuracy, reliability, and transparency in sourcing, while also guiding the format of the response to be 
            # clear and conversational for students.
            prompt = (
                "You are an assistant tasked with answering questions using only the information "
                "available in the provided documents. Your goal is to provide the most accurate "
                "and reliable answer possible based strictly on those sources.\n\n"

                "You are specifically a chatbot for the Virginia Commonwealth University (VCU) "
                "Computer Science Department. Your responses must prioritize official VCU sources "
                "such as the VCU Computer Science Department website and the VCU Bulletin.\n\n"

                "When discussing courses, you must follow these rules:\n"
                "- Only treat a course as valid if the source includes a detailed course description.\n"
                "- If a course name or course number appears without a full descriptive explanation, "
                "do NOT treat it as an available course and do NOT include it in your answer.\n"
                "- If the information is incomplete or only a list of course titles is shown, "
                "assume those courses are not confirmed and do not reference them.\n\n"

                "Whenever possible include the direct source URL used for the answer.\n\n"

                "If the answer cannot be found in the provided data, clearly state that the "
                "information is not available in the current sources.\n\n"

                "Do not fabricate information, courses, or URLs. CMSC 403 is not a class"
            )
            #Tell the model what style to use when answering
            format_style = (
                "Answer clearly and conversationally, as if explaining to a student."
            )
            # Combine the prompt, user question, and format instructions into a single input
            full_prompt = f"{prompt}\n\nQuestion: {question}\n\nFormat: {format_style}"
            
            # Query the vector index for most relevant answer to the user's question based on the combined prompt
            response = self.query_engine.query(full_prompt)

            #Return the response generated by the model
            return response.response

        except Exception as e:
            # Return an error message if there is something wrong with the query process
            return f"Error parsing query: {e}"
