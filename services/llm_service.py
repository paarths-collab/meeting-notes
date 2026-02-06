import os
import json
import warnings
from typing import Any, Optional
import google.generativeai as genai
from services.base import LLMService

# Suppress Gemini deprecation warning
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")
warnings.filterwarnings("ignore", category=FutureWarning, module="google.auth")


class GeminiLLMService(LLMService):
    """Gemini-based LLM service implementation."""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        """
        Initialize Gemini service.
        
        Args:
            api_key: Gemini API key
            model_name: Model to use (default: gemini-2.5-flash)
        """
        self.api_key = api_key
        self.model_name = model_name
        genai.configure(api_key=api_key)
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text response from Gemini."""
        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_prompt
        )
        
        response = model.generate_content(prompt)
        return response.text
    
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Any:
        """Generate JSON response from Gemini."""
        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        response = model.generate_content(prompt)
        cleaned_text = self._clean_json(response.text)
        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError:
            # Fallback: strict=False sometimes helps
            return json.loads(cleaned_text, strict=False)

    def _clean_json(self, text: str) -> str:
        """Remove invalid control characters from JSON string."""
        # Remove control characters (0-31) except newlines/tabs
        import re
        # Preserve \n \r \t
        return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
