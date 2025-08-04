from fastapi import APIRouter, Depends
from Qdrant.schemas import TableCreate, ColumnCreate
from Qdrant.services.TableService import TableService
from Qdrant.services.ColumnService import ColumnService
import logfire
router = APIRouter()

def get_table_service():
    return TableService()

@router.post("/create_table")
async def create_table(
    table: TableCreate, 
    service: TableService = Depends()
):
    with logfire.span("CreateTable function in TableControllers") as span:
        
        table_response = await service.create_table(table)
        return table_response

@router.get("/table/{table_id}")
async def get_table(
    table_id: str,
    service: TableService = Depends()
):
    table_response = await service.get_table(table_id)
    return table_response

@router.get("/table/")
async def get_tables(
    service: TableService = Depends()
):
    table_response = await service.get_tables()
    print(table_response)
    return table_response

@router.put("/table/{table_id}/")
async def update_table(
    table_id: str,
    table: TableCreate, 
    service: TableService = Depends()
):
    table_response = await service.update_table(table_id, table)
    return table_response

@router.delete("/table/{table_id}")
async def delete_table(
    table_id: str,
    service: TableService = Depends()
):
    table_response = await service.delete_table(table_id)
    return table_response
