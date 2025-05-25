from fastapi import APIRouter, HTTPException, Query, Body
from app.core.config import settings
from app.core.indexer import index_documents, get_index_stats
from app.services.search_service import search_content
from app.models.schema import SearchResponse, IndexingStatus, IndexStats, SearchRequest, SearchFilters

router = APIRouter()


@router.post("/index", response_model=IndexingStatus, tags=["Indexação"])
async def trigger_indexing():
    try:
        return index_documents(settings.DATA_DIRECTORY)
    except Exception as e:
        raise HTTPException(500, f"Indexing error: {str(e)}")


@router.get("/index/stats", response_model=IndexStats, tags=["Indexação"])
async def get_stats():
    try:
        return get_index_stats()
    except Exception as e:
        raise HTTPException(500, f"Stats error: {str(e)}")


@router.post("/search", response_model=SearchResponse, tags=["Busca"])
async def search_files(search_request: SearchRequest = Body(...)):
    try:
        results = search_content(search_request)
        if not results.results.items:
            raise HTTPException(
                404, f"No results for '{search_request.query}'")
        return results
    except FileNotFoundError:
        raise HTTPException(503, "Index not found - run /index first")
    except Exception as e:
        raise HTTPException(500, f"Search error: {str(e)}")


@router.get("/search", response_model=SearchResponse, tags=["Busca"])
async def search_files_get(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(settings.DEFAULT_PAGE_SIZE,
                           ge=1, le=settings.MAX_PAGE_SIZE),
    file_types: str = Query(None, description="Comma-separated file types"),
    min_score: float = Query(None, ge=0.0, le=1.0)
):
    try:
        filters = SearchFilters()
        if file_types:
            filters.file_types = [ft.strip() for ft in file_types.split(",")]
        if min_score is not None:
            filters.min_score = min_score

        search_request = SearchRequest(
            query=q,
            page=page,
            page_size=page_size,
            filters=filters if file_types or min_score else None
        )

        results = search_content(search_request)
        if not results.results.items:
            raise HTTPException(404, f"No results for '{q}'")
        return results
    except FileNotFoundError:
        raise HTTPException(503, "Index not found - run /index first")
    except Exception as e:
        raise HTTPException(500, f"Search error: {str(e)}")
