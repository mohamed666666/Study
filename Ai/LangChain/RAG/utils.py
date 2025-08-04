from langchain_ollama import OllamaEmbeddings
from langchain.chat_models import init_chat_model
from langchain_chroma import Chroma
import os
import getpass
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

# Load environment variables from .env
load_dotenv()

# Check if the API key is set; otherwise, prompt the user
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")



# Use OpenAI embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
# Initialize ChromaDB with the embeddings
vector_store = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)



# Get API key if not set
llm=init_chat_model("llama3-8b-8192", model_provider="groq",api_key="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")

print("Llama embedding model initialized successfully!")