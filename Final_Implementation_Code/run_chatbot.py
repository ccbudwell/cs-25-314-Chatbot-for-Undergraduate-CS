from chat3 import Chatbot

# Initialize the chatbot
bot = Chatbot(config_file="config.json")

print("Chatbot is ready! Type 'exit' to quit.\n")

while True:
    question = input("You: ")
    if question.lower() == "exit":
        response = bot.ask_response(question)
        print("Chatbot:", response)
        break
    response = bot.ask_response(question)
    print("Chatbot:", response)
 