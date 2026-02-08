import os
import requests
import mimetypes
from urllib.parse import urlparse
from fastapi import HTTPException

# Optional: Import transcription module if available
try:
    from backend.asr.whisper_transcriber import transcribe_audio
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False

def get_content_from_url(url: str) -> str:
    """Download content from URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        content_type = response.headers.get('Content-Type', '')
        
        # If it's text/html/json
        if 'text' in content_type or 'json' in content_type:
            return response.text
            
        # If it's audio/video and we have whisper
        if HAS_WHISPER and ('audio' in content_type or 'video' in content_type):
            # We need to save to temp file
            import tempfile
            suffix = mimetypes.guess_extension(content_type) or ".tmp"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name
            
            try:
                text = transcribe_audio(tmp_path)
                return text
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                    
        return response.text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")

def get_content_from_file(file_path: str) -> str:
    """Read content from local file path."""
    if not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="File not found")
        
    mime_type, _ = mimetypes.guess_type(file_path)
    
    # Text file
    if mime_type and ('text' in mime_type or 'json' in mime_type) or file_path.endswith(('.txt', '.md', '.py', '.js', '.html')):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="File must be text (UTF-8)")
            
    # Audio/Video
    if HAS_WHISPER and mime_type and ('audio' in mime_type or 'video' in mime_type):
        try:
            return transcribe_audio(file_path)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Transcription failed: {str(e)}")
            
    raise HTTPException(status_code=400, detail=f"Unsupported file type: {mime_type}")
