import time
from typing import List
from whoosh.qparser import MultifieldParser, AndGroup
from whoosh.highlight import UppercaseFormatter, ContextFragmenter
from whoosh import scoring
from app.core.indexer import get_index
from app.models.schema import SearchResponse, SearchResultItem, SearchRequest
from app.core.config import settings
from app.core.logger import logger
from app.utils.pagination import paginate_results
from app.utils.text_utils import truncate_text


class SearchService:
    def __init__(self):
        self.formatter = UppercaseFormatter()
        self.fragmenter = ContextFragmenter(
            maxchars=settings.HIGHLIGHT_MAX_CHARS,
            surround=settings.HIGHLIGHT_SURROUND
        )

    def _process_highlight(self, hit, path: str) -> str:
        try:
            raw_highlights = hit.highlights("content", top=1)
            if raw_highlights:
                return raw_highlights

            content = hit.get("content", "")
            return truncate_text(content, settings.HIGHLIGHT_MAX_CHARS)
        except Exception as e:
            logger.warning(f"Error generating highlights for {path}: {str(e)}")
            return "[Content unavailable]"

    def _build_searcher(self, ix):
        return ix.searcher(weighting=scoring.BM25F(B=0.75, K1=1.5))

    def _apply_filters(self, results, filters):
        if not filters:
            return results

        filtered = []
        for result in results:
            if filters.file_types and result.file_type not in filters.file_types:
                continue
            if filters.min_score and result.score < filters.min_score:
                continue
            filtered.append(result)

        return filtered

    def search_content(self, search_request: SearchRequest) -> SearchResponse:
        start_time = time.time()

        try:
            ix = get_index()
            results = []

            with self._build_searcher(ix) as searcher:
                query = MultifieldParser(
                    ["title", "content"],
                    schema=ix.schema,
                    group=AndGroup,
                    fieldboosts={"title": 3.0, "content": 1.0}
                ).parse(search_request.query)

                total_limit = search_request.page * search_request.page_size + 50
                results_obj = searcher.search(
                    query, limit=total_limit, terms=True)
                results_obj.formatter = self.formatter
                results_obj.fragmenter = self.fragmenter

                for hit in results_obj:
                    result_item = SearchResultItem(
                        title=hit.get("title", "Untitled"),
                        path=hit.get("path", "Unknown path"),
                        score=float(hit.score),
                        highlights=self._process_highlight(
                            hit, hit.get("path")),
                        file_type=hit.get("file_type", "unknown"),
                        size_preview=truncate_text(hit.get("content", ""), 100)
                    )
                    results.append(result_item)

                filtered_results = self._apply_filters(
                    results, search_request.filters)

                paginated_results = paginate_results(
                    filtered_results,
                    search_request.page,
                    search_request.page_size,
                    len(results_obj)
                )

                search_time = (time.time() - start_time) * 1000

                return SearchResponse(
                    query=search_request.query,
                    results=paginated_results,
                    search_time_ms=round(search_time, 2)
                )

        except FileNotFoundError:
            logger.error("Search index not found")
            raise
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            raise


search_service = SearchService()


def search_content(search_request: SearchRequest) -> SearchResponse:
    return search_service.search_content(search_request)
