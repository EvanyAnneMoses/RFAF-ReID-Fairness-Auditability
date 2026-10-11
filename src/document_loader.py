from pathlib import Path
from typing import Iterable, Dict, List


def load_path(path: str | Path) -> Dict[str, str]:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return {"name": path.name, "text": path.read_text(encoding="utf-8")}
    if suffix == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
        return {"name": path.name, "text": text}
    raise ValueError(f"Unsupported file type: {suffix}")


def load_many(paths: Iterable[str | Path]) -> List[Dict[str, str]]:
    return [load_path(p) for p in paths]
