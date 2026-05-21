from io import BytesIO
from pathlib import Path


SUPPORTED_EXTENSIONS = {".txt", ".docx", ".pdf"}


def _decode_text(contents: bytes) -> str:
    """优先 UTF-8，失败后用常见中文编码兜底。"""
    for encoding in ("utf-8", "utf-8-sig", "gb18030", "latin-1"):
        try:
            return contents.decode(encoding)
        except UnicodeDecodeError:
            continue
    return contents.decode("utf-8", errors="replace")


def parse_uploaded_file(filename: str, contents: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {suffix}. Supported: txt, docx, pdf")

    if suffix == ".txt":
        return _decode_text(contents).strip()

    if suffix == ".docx":
        try:
            from docx import Document
        except ImportError as exc:
            raise ValueError("python-docx is required to parse docx files. Install backend requirements first.") from exc
        document = Document(BytesIO(contents))
        return "\n".join(p.text for p in document.paragraphs if p.text.strip()).strip()

    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ValueError("pypdf is required to parse pdf files. Install backend requirements first.") from exc
    reader = PdfReader(BytesIO(contents))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()


def parse_file(path: str | Path) -> str:
    file_path = Path(path)
    return parse_uploaded_file(file_path.name, file_path.read_bytes())
