"""
URL Download Helper

Downloads files from URLs for processing.
"""
import requests
import os


def download_file(url: str, save_path: str = "inputs/downloads/recording.mp4") -> str:
    """
    Download file from URL.
    
    Args:
        url: URL to download from
        save_path: Local path to save file
        
    Returns:
        Path to downloaded file
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    r = requests.get(url, stream=True)
    r.raise_for_status()

    with open(save_path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)

    return save_path
