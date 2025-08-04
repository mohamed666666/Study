from fastapi import FastAPI
from Qdrant.controllers.ColumnControllers import router as columns_router
from Qdrant.controllers.TableControllers import router as tables_router
from Qdrant.controllers.SearchCotrollers import router as search_router
import logfire
from logging import basicConfig

from contextlib import asynccontextmanager
from qdrant_client import AsyncQdrantClient


logfire.configure(token='pylf_v1_us_lffks9kNKQDTjkCqpHZBJLVzzPfVZxptfkVD53TShlS8',inspect_arguments=False)
#logfire.instrument_pydantic()  

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.qdrant_client = AsyncQdrantClient(url="http://localhost:6333")
        await app.state.qdrant_client.get_collections()  # Test connection
        yield
    except Exception as e:
        logfire.error(f"Qdrant connection failed: {e}")
        raise
    finally:
        if hasattr(app.state, 'qdrant_client'):
            await app.state.qdrant_client.close()


app = FastAPI(debug=True,lifespan=lifespan)
logfire.instrument_fastapi(app, capture_headers=True)
app.include_router(search_router, prefix="/search", tags=["search"])
app.include_router(tables_router, prefix="/tables", tags=["tables"])
app.include_router(columns_router, prefix="/columns", tags=["columns"])
def main()->None:
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()