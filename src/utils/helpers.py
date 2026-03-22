

import hashlib
import time

def load_yaml(file_path):
    """Load a YAML file and return its contents as a dictionary."""
    import yaml

    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file) or {}
    
def hash_text(text: str) -> str:
    """Return a SHA256 hash of a String (used as a document id)."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]  # Use first 16 chars for brevity

def elapsed_ms(start: float) -> int:
    """Return elapsed milliseconds since start (from time.time())."""
    return int((time.time() - start) * 1000)