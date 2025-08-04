from mcp.server.fastmcp import FastMCP
import arxiv
import os
import json
from typing import List
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional
from sqlalchemy import Column

mcp = FastMCP("db_server")#must be mcp 





@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    """
    Health check endpoint for the service.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        PlainTextResponse: A simple response with the text "OK" to indicate the service is running.
    """
    return PlainTextResponse("OK")

# SQLModel ORM class for chapters table
class Chapter(SQLModel, table=True):
    __tablename__ = "chapters"
    id: Optional[int] = Field(default=None, primary_key=True)
    name_ar: Optional[str]
    name_pron_en: Optional[str]
    class_: Optional[str] = Field(sa_column=Column("class", default=None))
    verses_number: Optional[int]
    content: Optional[str]

# Database URL
DB_PATH = "/home/v/Work/Realsoft/Mosaad_ElKhateeb/khateeb-ai-assistant/swifi/db/swer_quran.sqlite"
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)


@mcp.tool()
async def retrive_all_swer() -> list[Chapter]:
    """
    Retrieve all chapters from the 'chapters' table in the database.

    Returns:
        list[Chapter]: A list of Chapter objects representing all rows in the 'chapters' table.
    """
    with Session(engine) as session:
        statement = select(Chapter)
        results = session.exec(statement).all()
        return results


@mcp.tool()
async def search_ayah(text: str) -> list[Chapter]:
    """
    Search for ayahs in the 'content' field of the 'chapters' table that contain the given text.

    Args:
        text (str): The text to search for within the 'content' field.

    Returns:
        list[Chapter]: A list of Chapter objects where the 'content' field contains the specified text.
    """
    with Session(engine) as session:
        statement = select(Chapter).where(Chapter.content.like(f"%{text}%"))
        results = session.exec(statement).all()
        return results


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run()
