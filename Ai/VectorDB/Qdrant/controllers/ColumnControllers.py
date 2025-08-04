from fastapi import APIRouter,Depends
from Qdrant.schemas import TableCreate,ColumnCreate
from Qdrant.services.TableService import TableService
from Qdrant.services.ColumnService import ColumnService
import asyncio

router = APIRouter()

def get_column_service():
    return ColumnService()



@router.post("/columns/{table_id}")
async def create_column(table_id: str, 
                        column: ColumnCreate,
                        service:ColumnService =Depends(get_column_service),):
   
    new_column = await service.create_column(table_id=table_id, column=column)
    return new_column