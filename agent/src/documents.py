"""Document loader for trip data files."""

from pathlib import Path


def load_documents(data_dir: Path | None = None) -> dict[str, str]:
    """Load all .txt files from data directory.

    Args:
        data_dir: Directory containing .txt files. Defaults to ./data/

    Returns:
        Dictionary mapping filename (without .txt) to file content.
        Example: {"flight": "...", "car_rental": "..."}

    Raises:
        FileNotFoundError: If data_dir does not exist
    """
    if data_dir is None:
        # Default to data/ directory relative to this file's parent
        data_dir = Path(__file__).parent.parent / "data"

    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    documents: dict[str, str] = {}

    # Load all .txt files from the directory
    for txt_file in data_dir.glob("*.txt"):
        # Use stem to get filename without extension
        key = txt_file.stem
        documents[key] = txt_file.read_text(encoding="utf-8")

    return documents
