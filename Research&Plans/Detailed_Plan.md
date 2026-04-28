## Chatbot for Computer Science

*Below will be the detailed plan for implementation onto the VCU  website.

1) Python program that utilzes Apify for web scraping and RAG techniques for word processing and conversation functionality. 
    
2) User Interface: Add HTML to the VCU pages that we want the chatbot to appear under
  - Chatbot user interface will be in a container within the HTML page and will send message information entered by the user to the backend which will then query       the database using the chatbot to be implemented.
  - Also will populate the chatbot's responses to the user in the container
  - HTML code for the div:
     ![image](https://github.com/user-attachments/assets/08855de0-e1aa-4ab9-b949-43ae472e7b93)

    
  - Uses .js for fetching the text from the user-input and populates the return of the python program in the backend to jsonify the chatbot's response and repopulate it in the chatbot container
  - Uses .css for the design of the visual and user experience portion on the website.
    
**All code for this project is in the Final_Implementation_Code folder**
Dave Duncan- i just increased the chatbots intelligence by like 30% id say it sits around a 60/70% effectiveness heres the workflow that i set up
VCU Websites
      │
      ▼
Web Scraping
(requests + BeautifulSoup)
      │
      ▼
Extract
• Text
• Tables
• Images
      │
      ▼
Tables → Natural Language
      │
      ▼
Create Documents
      │
      ▼
OpenAI Embeddings
(text-embedding-3-large)
      │
      ▼
Vector Database
(LlamaIndex)
      │
      ▼
User Question
      │
      ▼
Vector Search
      │
      ▼
LLM Generates Answer
      │
      ▼
Chatbot Response
this workflow takes out apify webscraper entirely reducing the cost of the project to just openai
it uses requests + BeautifulSoup + pandas to extract text tables and images from each of the urls. after it combines all the information into one document which is then injested into the vector database and the images has its own DB. these are used to answer the questions ask DR.budwell for rubric from 2026s team discord for testing rubric for evaluation. this is just example of how to evaluate it you need to create another one to increase the understanding of the chatbots performance.
























