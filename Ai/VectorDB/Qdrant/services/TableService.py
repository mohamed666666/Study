# table_service.py
from Qdrant.schemas import TableCreate, Table, Column, ColumnCreate, TableResponse
import json
import uuid
from fastapi import HTTPException, Depends
from Qdrant.services.QdrantService import QdrantService
from typing import List, Optional
import logfire

class TableService:
    def __init__(self, collection_name: str = "tables_collection", qdrant_service: QdrantService = Depends()):
        with logfire.span("Initialize TableService") as span:
            self.__qdrant_service = qdrant_service
            self.__collection_name = collection_name
            span.set_attributes({
                "collection_name": collection_name,
                "qdrant_service": type(qdrant_service).__name__
            })
            logfire.info("TableService initialized", name="table service initialized")

    async def create_table(self, table: TableCreate) -> TableResponse:
        with logfire.span("CreateTable function inTableService") as span:
            try:
                span.set_attributes({
                    "table_name": table.name,
                    "columns_count": len(table.columns)
                })
                
                generated_table_id = str(uuid.uuid4())
                columns_with_id = [
                    Column(
                        id=str(uuid.uuid4()),
                        name=col.name,
                        alias=col.alias,
                        description=col.description,
                        data_type=col.data_type,
                        is_nullable=col.is_nullable,
                        is_primary_key=col.is_primary_key,
                        is_foreign_key=col.is_foreign_key,
                        foreign_key_table_id=col.foreign_key_table_id,
                        is_unique=col.is_unique,
                        is_indexable=col.is_indexable,
                        is_searchable=col.is_searchable,
                        is_filterable=col.is_filterable,
                    )
                    for col in table.columns
                ]
                
                table_json = {
                    "id": generated_table_id,
                    "content": json.dumps(table.model_dump()),
                    "payload": table.model_dump()
                }
                
                with logfire.span("QdrantUpsert "):
                    await self.__qdrant_service.add_points(self.__collection_name, [table_json])
                
                logfire.info("Table created in TableService", 
                            table_id=generated_table_id,
                            columns_count=len(columns_with_id))
                
                return TableResponse(
                    id=generated_table_id,
                    name=table.name,
                    alias=table.alias,
                    description=table.description,
                    columns=columns_with_id
                )
            except Exception as e:
                logfire.record_exception(e)
                span.set_level("error")
                raise HTTPException(status_code=500, detail=f"Failed to create table: {str(e)}")
   
    async def get_table(self, table_id: str):
        with logfire.span("GetTable") as span:
            span.set_attribute("table_id", table_id)
            logfire.info("Getting table", table_id=table_id,name="get table by its id")
            try:
                result = await self.__qdrant_service.get_point(self.__collection_name, table_id)
                if not result:
                    logfire.warning("Table not found", table_id=table_id)
                    raise HTTPException(status_code=404, detail="Table not found")
                return result[0].payload
            except Exception as e:
                logfire.record_exception(e)
                span.set_level("error")
                raise HTTPException(status_code=500, detail=f"Error retrieving table: {str(e)}")

    async def get_tables(self) -> List[Optional[TableResponse]]:
        with logfire.span("GetAllTables") as span:
            try:
                tables = await self.__qdrant_service.get_all_points(self.__collection_name)
                span.set_attribute("tables_count", len(tables))
                return [table.payload for table in tables]
            except Exception as e:
                logfire.record_exception(e)
                span.set_level("error")
                raise HTTPException(status_code=500, detail=f"Error retrieving tables: {str(e)}")

    async def delete_table(self, table_id: str):
        with logfire.span("DeleteTable") as span:
            span.set_attribute("table_id", table_id)
            try:
                with logfire.span("QdrantDelete"):
                    await self.__qdrant_service.delete_point(self.__collection_name, table_id)
                logfire.info("Table deleted", table_id=table_id)
            except Exception as e:
                logfire.record_exception(e)
                span.set_level("error")
                error_msg = str(e).lower()
                if "not found" in error_msg:
                    raise HTTPException(status_code=400, detail="Table does not exist")
                else:
                    raise HTTPException(status_code=500, detail=f"Failed to delete table: {str(e)}")

    async def update_table(self, table_id: str, table: TableCreate) -> TableResponse:
        with logfire.span("UpdateTable") as span:
            span.set_attributes({
                "table_id": table_id,
                "new_name": table.name,
                "columns_updated": len(table.columns)
            })
            try:
                updated_table_json = {
                    "id": table_id,
                    "content": json.dumps(table.model_dump()),
                    "payload": table.model_dump()
                }
                
                with logfire.span("QdrantUpdate"):
                    updated = await self.__qdrant_service.update_point(
                        self.__collection_name, table_id, updated_table_json
                    )
                
                if not updated:
                    logfire.warning("Update failed - table not found", table_id=table_id)
                    raise HTTPException(status_code=404, detail="Table not found")
                
                logfire.info("Table updated", table_id=table_id)
                return updated
            except Exception as e:
                logfire.record_exception(e)
                span.set_level("error")
                error_msg = str(e).lower()
                if "not found" in error_msg:
                    raise HTTPException(status_code=400, detail="Table does not exist")
                else:
                    raise HTTPException(status_code=500, detail=f"Failed to update table: {str(e)}")