from typing import List
import dis
import os
import getpass
if not os.environ.get("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = getpass.getpass("Enter API key for Groq: ")
    
from langchain.chat_models import init_chat_model
from langchain.schema import HumanMessage, SystemMessage

def create_chat_model():
    return init_chat_model("llama3-8b-8192", model_provider="groq",api_key="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")

def main():
    model = create_chat_model()
    messages = [
        SystemMessage(content="You are a helpful AI assistant.")
    ]
    
    print("Welcome to the chat! Type 'quit' to exit.")
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == 'quit':
            print("Goodbye!")
            print(messages)
            break
            
        messages.append(HumanMessage(content=user_input))
        
        try:
            response = model.invoke(messages)
            print("\nAssistant:", response.content)
            messages.append(response)
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()