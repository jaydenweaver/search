from pathlib import Path

def load_checkpoint(path: Path) -> str | None:
    if path.exists():
        return path.read_text().strip() or None
    return None

def save_checkpoint(path: Path, last_id: str):
    path.write_text(last_id)