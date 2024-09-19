import os

def load_audio_file(file_path):
    """Load the specified audio file and return its path."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    return file_path
