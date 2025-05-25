from typing import TypeVar, Generic, List
from pydantic import BaseModel
from math import ceil

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


def paginate_results(items: List[T], page: int, page_size: int, total_count: int = None) -> PaginatedResponse[T]:
    if total_count is None:
        total_count = len(items)

    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size

    paginated_items = items[start_idx:end_idx]
    total_pages = ceil(total_count / page_size) if page_size > 0 else 1

    return PaginatedResponse(
        items=paginated_items,
        total=total_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1
    )
