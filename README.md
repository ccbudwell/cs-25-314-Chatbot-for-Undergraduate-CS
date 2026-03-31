# VCU Computer Science Chatbot

## Overview

This project is a chatbot designed to answer questions related to the VCU Computer Science department. The chatbot uses a retrieval-based approach, combining web scraping, vector embeddings, and a language model to generate responses based on official VCU sources.

The goal is to provide accurate and relevant answers to student questions such as course information, program details, and department resources.

---

## Features

- Retrieval-based chatbot using VCU data
- Web scraping of official department pages
- Vector search using embeddings for context retrieval
- Real-time chat interface using WebSockets
- Logging for debugging and monitoring

---

## How It Works

1. User sends a message through the chat interface  
2. The message is sent to the backend via WebSocket  
3. The backend converts the query into an embedding  
4. Relevant content is retrieved from the vector index  
5. A response is generated using the retrieved context  
6. The response is sent back and displayed  

---

## Setup

Install dependencies:

pip install torch torchvision llama-index openai apify-client

Create a file called:

keys.env

Add your API keys:

OPENAI_API_KEY=your_key_here  
APIFY_API_KEY=your_key_here  

Run the chatbot:

python main.py

---

## Notes

- Do not upload keys.env to GitHub  
- storage_index/ and chatbot.log should not be committed  
- The chatbot may have limited accuracy for course-specific questions  

---

## Future Improvements

- Add structured course data  
- Improve query understanding  
- Add source attribution  
- Improve UI and deploy the system  

---

## Team Members

Dave Duncan  
Devin Hale  
Sofianas Fondja  
Sameer Ali

# *Chatbot for CS*
## *Virginia Commonwealth University*
## *Create a chatbot that can be implemented on the VCU website. The target audience/user for the chatbot would be undergraduate students in the Computer Science program.*

| Folder | Description |
|---|---|
| Final_Implementation_Code | Holds all final code for implementation |
| Research & Plans | Relevant research, design document, and sources or project |
| Project Deliverables | Folder that contains final pdf versions of all Fall and Spring Major Deliverables |
| Status Reports | Project management documentation - weekly reports, milestones, etc. |


## Project Team
- *Caroline Budwell* - *Computer Science* - Faculty Advisor
- *Kennedy Martin* - *Computer Science* - Student Team Member
- *Antony Fuentes* - *Computer Science* - Student Team Member
- *Israel Agoe-Sowah* - *Computer Science* - Student Team Member
- *Eric Simoni* - *Computer Science* - Student Team Member
