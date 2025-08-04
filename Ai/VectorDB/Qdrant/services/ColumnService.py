from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams,Distance
from Qdrant.managers import QdrantManager
from typing import List
from qdrant_client.http.models import PointStruct
from Qdrant.embeddings import Embeddings
from Qdrant.schemas import TableCreate,Table,  Column, ColumnCreate,TableResponse
import json
import uuid
from Qdrant.services.QdrantService import QdrantService
        
from Qdrant.services.QdrantService import QdrantService
from typing import List, Optional
import json
import uuid
from Qdrant.schemas import TableCreate, Table, Column, ColumnCreate, TableResponse

class ColumnService:
    def __init__(self):
        self.__qdrant_service = QdrantService()  # Assumes async methods are available
        self.__table_collection = "tables_collection"

    async def create_column(self, table_id: str, column: ColumnCreate) -> Column:
        try:
            # 1. Get the existing table asynchronously.
            table_points = await self.__qdrant_service.get_point(self.__table_collection, table_id)
            if not table_points or len(table_points) == 0:
                raise ValueError(f"Table {table_id} not found")

            # 2. Copy payload and ensure defaults.
            payload = table_points[0].payload.copy()
            if "id" not in payload:
                payload["id"] = table_id
            if "columns" not in payload:
                payload["columns"] = []
            else:
                # Ensure every column has an 'id'
                for col in payload["columns"]:
                    if "id" not in col:
                        col["id"] = "default-column-id"

            table_data = TableResponse(**payload)
            
            # 3. Generate a new column ID.
            column_id = str(uuid.uuid4())

            # 4. Handle foreign key table lookup.
            fk_table = None
            if column.foreign_key_table_id:
                fk_points = await self.__qdrant_service.get_point(
                    self.__table_collection, column.foreign_key_table_id
                )
                if fk_points and len(fk_points) > 0:
                    fk_table = Table(**fk_points[0].payload)
            
            # 5. Create the new Column object.
            new_column = Column(
                id=column_id,
                name=column.name,
                alias=column.alias,
                table_id=table_id,
                description=column.description,
                data_type=column.data_type,
                is_nullable=column.is_nullable,
                is_primary_key=column.is_primary_key,
                is_foreign_key=column.is_foreign_key,
                foreign_key_table_id=fk_table.id if fk_table else None,
                is_unique=column.is_unique,
                is_indexable=column.is_indexable,
                is_searchable=column.is_searchable,
                is_filterable=column.is_filterable
            )

            # 6. Update table's columns list.
            updated_columns = table_data.columns + [new_column]
            updated_table = table_data.model_copy(update={"columns": updated_columns})
            
            # 7. Prepare the updated document.
            updated_doc = {
                "id": table_id,
                "content": json.dumps(updated_table.model_dump()),
                "payload": updated_table.model_dump()
            }

            # 8. Update the table in Qdrant asynchronously.
            await self.__qdrant_service.update_point(
                collection_name=self.__table_collection,
                point_id=table_id,
                newdoc=updated_doc
            )

            return new_column

        except Exception as e:
            raise RuntimeError(f"Column creation failed: {str(e)}")

    async def get_column(self, column_id: int):
        # Implementation needed
        pass

    async def get_columns(self):
        # Implementation needed
        pass

    async def get_table_columns(self, table_id: int):
        # Implementation needed
        pass

    async def delete_column(self, column_id: int):
        # Implementation needed
        pass
