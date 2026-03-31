# Project Overview
The project is a chatbot designed for the VCU Computer Science Department website. The goal of the chatbot is to help user find accurate information about topics such as:
- Degree Programs
- Courses
- Department Resources
- General CS-related Information

The chatbot works by:
1. Scraping official VCU websites for relevant information
2. Processing and storing the data using vector embeddings
3. Answering user questions by searching through that indexed data

The system is built using:
- Python for backend logic
- FastAPI for the web server and API endpoints
- LlamaIndex + OpenAI embeddings for semantic search
- Web scraping tools (Beautiful Soup, requests, pandas) for data collection
- WebSockets for real-time chat functionality

Overall, the chatbot aims to provide a fast and reliable way for students to acess important CS department information.

# Challenges & Solutions

## Main Challenge
One of the biggest challenges we faced during this project was that the chatbot did not always provide accurate
and complete answers. After investigating the issue, we determined the root cause was incomplete web scraping.
The chatbot relies heavily on scraped data to build its knowledge base, and if important content is missing,
the responses become unreliable or partially correct.

# Solutions Implemented
To address this issue, we explored multiple approaches:

1. Improved Scaping Visibilty (Apify)
We created an account with Apify, which allowed us to better monitor and track scraping process. This 
helped us understand:
- Which pages were being scraped successfully
- Where data was missing or incomplete
- How much content was actually being collected
This step was important for diagnosing the problem rather than just guessing

2. Evaluated Alternative Scrapers
We looked into other web scraping tools and services that could potentially improve data collection.
However, most of the reliable options were too expensive for our project's constraints, so we decided
not to persue them any further.

3. Optimized Chatbot Processing (chat3.py)
Since improving the scraper itself was limited, we shifted focus to how the chatbot uses the available data.

We updated chat3.py to:
- Better structure and combine scraped content
- Improve how tables and page data are converted into readable text
- Strengthen prompt instructions to reduce incorrect answers
These improvements made the chatbot more efficient when working with imperfect data

4. Expanded Data Sources
We added more VCU related links to the "config.json" file. This allowed the chatbot to:
- Access a wider range of information
- Improve coverage of topics
- Reduce missing answers due to lack of data

# Current Performance
After implementing these improvements, the chatbot is now approximately:
- 70-80% accurate

While this is a significant improvement from ealier versions, it is still below the 95% accuracy requirement
needed for deployment on the official VCU website.

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
