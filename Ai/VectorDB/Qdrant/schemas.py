from pydantic import BaseModel, Field
from typing import List, Optional

class TableBase(BaseModel):
    name: str = Field(..., description="The name of the table")
    alias: str = Field(..., description="The alias of the table")
    description: str = Field(..., description="The description of the table")

class ColumnBase(BaseModel):
    name: str = Field(..., description="The name of the column")
    alias: str = Field(..., description="The alias of the column")
    description: str = Field(..., description="The description of the column")
    data_type: str = Field(..., description="The data type of the column")
    is_nullable: bool = Field(..., description="Indicates if the column can be null")
    is_primary_key: bool = Field(..., description="Indicates if the column is a primary key")
    is_foreign_key: bool = Field(..., description="Indicates if the column is a foreign key")
    foreign_key_table_id: Optional[str] = Field(None, description="The ID of the table for the foreign key")
    is_unique: bool = Field(..., description="Indicates if the column has a unique constraint")
    is_indexable: bool = Field(..., description="Indicates if the column is indexable")
    is_searchable: bool = Field(..., description="Indicates if the column is searchable")
    is_filterable: bool = Field(..., description="Indicates if the column is filterable")
    
    
class TableCreate(TableBase):
    # For creation, you only need the base fields plus the list of columns
    columns: List['ColumnCreate'] = Field(..., description="The list of columns in the table")

class ColumnCreate(ColumnBase):
    # For creation, you use the base fields; no ID is needed because it will be generated.
    pass
class Table(TableBase):
    id: str = Field(..., description="The unique identifier of the table")

class Column(ColumnBase):
    id: str = Field(..., description="The unique identifier of the column")

class TableResponse(Table):
    columns: List[Column] = Field(..., description="The list of columns in the table")
