import os
import time
from pathlib import Path
from typing import Set, Tuple, List
from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, TEXT, ID, DATETIME
from whoosh.analysis import LanguageAnalyzer
from app.core.config import settings
from app.core.logger import logger
from app.services.file_parser import parse_file, get_supported_formats
from app.utils.path_utils import ensure_directory_exists, is_temp_file, get_file_extension

pt_analyzer = LanguageAnalyzer("pt")
INDEX_SCHEMA = Schema(
    title=TEXT(stored=True, analyzer=pt_analyzer),
    path=ID(stored=True, unique=True),
    content=TEXT(stored=True, analyzer=pt_analyzer),
    file_type=TEXT(stored=True),
    indexed_at=DATETIME(stored=True)
)


class IndexManager:
    def __init__(self, index_dir: str = settings.INDEX_DIR):
        self.index_dir = ensure_directory_exists(index_dir)
        self._index = None

    def get_index(self):
        if self._index is None:
            if exists_in(str(self.index_dir)):
                self._index = open_dir(str(self.index_dir))
            else:
                self._index = create_in(str(self.index_dir), INDEX_SCHEMA)
        return self._index

    def get_existing_paths(self) -> Set[str]:
        try:
            ix = self.get_index()
            with ix.reader() as reader:
                return {fields['path'] for fields in reader.all_stored_fields()}
        except Exception as e:
            logger.warning(f"Error reading existing index: {str(e)}")
            return set()

    def get_stats(self) -> dict:
        try:
            ix = self.get_index()
            with ix.reader() as reader:
                total_docs = reader.doc_count()

            index_size = sum(
                f.stat().st_size for f in self.index_dir.rglob('*') if f.is_file())
            index_size_mb = index_size / (1024 * 1024)

            return {
                "total_documents": total_docs,
                "index_size_mb": round(index_size_mb, 2),
                "supported_formats": get_supported_formats()
            }
        except Exception as e:
            logger.error(f"Error getting index stats: {str(e)}")
            return {"total_documents": 0, "index_size_mb": 0.0, "supported_formats": []}


class DocumentIndexer:
    def __init__(self, index_manager: IndexManager):
        self.index_manager = index_manager

    def process_file(self, writer, file_path: Path, existing_paths: Set[str]) -> Tuple[int, int, List[str]]:
        if get_file_extension(file_path) not in get_supported_formats():
            return 0, 0, []

        content = parse_file(file_path)
        if not content:
            return 0, 0, [f"No content extracted from {file_path}"]

        try:
            from datetime import datetime
            writer.update_document(
                title=file_path.name,
                path=str(file_path),
                content=content,
                file_type=get_file_extension(file_path),
                indexed_at=datetime.now()
            )

            is_update = str(file_path) in existing_paths
            return (1, 0, []) if is_update else (0, 1, [])
        except Exception as e:
            error_msg = f"Indexing error for {file_path}: {str(e)}"
            logger.error(error_msg)
            return 0, 0, [error_msg]

    def index_documents(self, data_directory: str = settings.DATA_DIRECTORY) -> dict:
        start_time = time.time()
        ix = self.index_manager.get_index()

        writer = ix.writer(
            timeout=300,
            limitmb=256,
            procs=os.cpu_count(),
            multisegment=True
        )

        existing_paths = self.index_manager.get_existing_paths()
        indexed = updated = 0
        errors = []

        try:
            for root, _, files in os.walk(data_directory):
                for file in files:
                    if is_temp_file(file):
                        continue

                    file_path = Path(root) / file
                    u, i, file_errors = self.process_file(
                        writer, file_path, existing_paths)
                    updated += u
                    indexed += i
                    errors.extend(file_errors)

            writer.commit()
            total_time = time.time() - start_time

            logger.info(
                f"Indexing completed: {indexed} new, {updated} updated in {total_time:.2f}s")

            return {
                "message": "Indexing completed successfully",
                "indexed_files": indexed,
                "updated_files": updated,
                "total_time_seconds": round(total_time, 2),
                "errors": errors[:10] if errors else None
            }

        except Exception as e:
            logger.error(f"Commit failed: {str(e)}")
            raise


index_manager = IndexManager()
document_indexer = DocumentIndexer(index_manager)


def get_index():
    return index_manager.get_index()


def index_documents(data_directory: str = settings.DATA_DIRECTORY):
    return document_indexer.index_documents(data_directory)


def get_index_stats():
    return index_manager.get_stats()
