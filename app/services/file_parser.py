import docx
import PyPDF2
from markdown import markdown
from bs4 import BeautifulSoup
from pathlib import Path
from typing import List, Optional, Dict, Callable
from app.core.logger import logger


def extract_text_from_docx(file_path: str) -> str:
    try:
        doc = docx.Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        logger.error(f"Error parsing DOCX {file_path}: {str(e)}")
        return ""


def extract_text_from_pdf(file_path: str) -> str:
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text.strip():
                    text.append(page_text)
            return '\n'.join(text)
    except Exception as e:
        logger.error(f"Error parsing PDF {file_path}: {str(e)}")
        return ""


def extract_text_from_txt(file_path: str) -> str:
    try:
        encodings = ['utf-8', 'latin-1', 'cp1252']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        return ""
    except Exception as e:
        logger.error(f"Error parsing TXT {file_path}: {str(e)}")
        return ""


def extract_text_from_md(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
            html = markdown(md_content)
            return BeautifulSoup(html, 'html.parser').get_text()
    except Exception as e:
        logger.error(f"Error parsing MD {file_path}: {str(e)}")
        return ""


FILE_PARSERS: Dict[str, Callable[[str], str]] = {
    ".docx": extract_text_from_docx,
    ".pdf": extract_text_from_pdf,
    ".txt": extract_text_from_txt,
    ".md": extract_text_from_md
}


def get_supported_formats() -> List[str]:
    return list(FILE_PARSERS.keys())


def parse_file(file_path: Path) -> Optional[str]:
    parser = FILE_PARSERS.get(file_path.suffix.lower())
    if not parser:
        return None

    content = parser(str(file_path))
    return content if content.strip() else None
