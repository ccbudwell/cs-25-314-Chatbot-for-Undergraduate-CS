# Chatbot Final Implementation

## Overview

This folder contains the final working version of the VCU Computer Science chatbot. It includes both the backend logic for processing queries and the frontend interface for user interaction.

---

## How to Run

### 1. Install Dependencies

pip install torch torchvision llama-index openai apify-client

---

### 2. Set Up API Keys

Create a file named:

keys.env

Add your keys:

OPENAI_API_KEY=your_key_here  
APIFY_API_KEY=your_key_here  

---

### 3. Start the Backend

python main.py

This will start the chatbot server (WebSocket runs on ws://localhost:8000/ws).

---

### 4. Open the Frontend

- Open the HTML page that includes chatbot.js and styles.css  
- The chatbot will automatically connect to the backend  
- Type a message and press Enter or click Send  

---

## How It Works (Quick)

- Frontend sends message via WebSocket  
- Backend processes query using embeddings + vector search  
- Response is generated using retrieved context  
- Response is sent back and displayed in chat  

---

## Important Notes

- Do NOT commit keys.env  
- storage_index/ is generated automatically  
- chatbot.log stores logs for debugging  
- If data sources change, the index may need to be rebuilt  

---

## Troubleshooting

- If chatbot doesn’t respond → make sure backend is running  
- If WebSocket fails → check port 8000  
- If answers seem wrong → index may need to be refreshed  

---

## For Next Team

- Improve accuracy by adding structured course data  
- Add source links to responses  
- Implement index refresh system  
- Improve frontend UI  

