from pydantic import BaseModel, Field
from typing import List, Optional
from app.utils.pagination import PaginatedResponse


class SearchResultItem(BaseModel):
    title: str
    path: str
    score: Optional[float] = None
    highlights: Optional[str] = None
    file_type: Optional[str] = None
    size_preview: Optional[str] = None


class SearchFilters(BaseModel):
    file_types: Optional[List[str]] = None
    min_score: Optional[float] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=50)
    filters: Optional[SearchFilters] = None


class SearchResponse(BaseModel):
    query: str
    results: PaginatedResponse[SearchResultItem]
    search_time_ms: Optional[float] = None
    suggestions: Optional[List[str]] = None


class IndexingStatus(BaseModel):
    message: str
    indexed_files: Optional[int] = None
    updated_files: Optional[int] = None
    total_time_seconds: Optional[float] = None
    errors: Optional[List[str]] = None


class IndexStats(BaseModel):
    total_documents: int
    index_size_mb: float
    last_updated: Optional[str] = None
    supported_formats: List[str]
