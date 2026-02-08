import os
import json
import warnings

# Suppress Gemini deprecation warning BEFORE import
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*google.generativeai.*")

from typing import Any, Optional
import google.generativeai as genai
from backend.services.base import LLMService


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
            # Force JSON mode if supported by model version
            generation_config={"response_mime_type": "application/json"}
        )
        
        response = model.generate_content(prompt)
        text = response.text
        
        # 1. Remove Markdown code blocks
        if "```" in text:
            import re
            # Extract content between ```json ... ``` or just ``` ... ```
            match = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
            if match:
                text = match.group(1)
        
        cleaned_text = self._clean_json(text.strip())
        
        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError:
            # Fallback 1: Try ast.literal_eval for single quotes
            try:
                import ast
                return ast.literal_eval(cleaned_text)
            except (ValueError, SyntaxError):
                pass
                
            # Fallback 2: Try to repair common JSON errors
            pass
            
        return {}

    def _clean_json(self, text: str) -> str:
        """Remove invalid control characters from JSON string."""
        import re
        # Remove control characters (0-31) except newlines/tabs/returns
        return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
