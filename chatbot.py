from openai import OpenAI

# Initialize client with your API key
client = OpenAI(api_key="your_api_key_here")  # paste your key here

print("🤖 AI Chatbot: Hello! Type 'bye' to exit.")
conversation = []  # to store chat history

while True:
    user = input("You: ")
    if user.lower() == "bye":
        print("🤖 AI Chatbot: Goodbye!")
        break

    # Add user message to conversation
    conversation.append({"role": "user", "content": user})

    # Send chat history to the model
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # you can change to gpt-4o if available
        messages=conversation
    )

    # Extract reply text
    reply = response.choices[0].message.content
    print("🤖 AI Chatbot:", reply)

    # Add bot reply to conversation
    conversation.append({"role": "assistant", "content": reply})
