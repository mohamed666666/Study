from fastapi import FastAPI, Body
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from Orchastrator_agent import generate_sermon_async
import os
from google.adk.cli.fast_api import get_fast_api_app
from dotenv import load_dotenv

# Set up paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
AGENT_DIR = BASE_DIR  # Parent directory containing multi_tool_agent

# Set up DB path for sessions
SESSION_DB_URL = f"sqlite:///{os.path.join(BASE_DIR, 'sessions.db')}"

# Create the FastAPI app using ADK's helper
app = FastAPI()

class QueryRequest(BaseModel):
    query: str
"""
    @app.post("/serach/agent")
    async def handle_query(request: QueryRequest):
    # Process the query using the async runner
    print(f"Received query: {request.query}")
    result = await process_query_async(request.query)
    return JSONResponse(content={"result": result})"""


@app.post("/khatib/agent")
async def handle_khatib_query(request: QueryRequest):
    # Process the query using the async runner
    print(f"Received query: {request.query}")
    result = await generate_sermon_async(request.query)
    return JSONResponse(content={"result": result})