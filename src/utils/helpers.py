

import hashlib

def load_yaml(file_path):
    """Load a YAML file and return its contents as a dictionary."""
    import yaml

    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file) or {}
    
def hash_text(text: str) -> str:
    """Return a SHA256 hash of a String (used as a document id)."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]  # Use first 16 chars for brevity