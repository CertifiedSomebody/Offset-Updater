from typing import Optional
from google import genai
from ..core.config import Config


class GeminiAPI:
    """
    Gemini API wrapper using the official google-genai SDK (2025).
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.get_api_key()
        if not self.api_key:
            raise ValueError(
                "Gemini API key is required. Set it using Config.set_api_key() or in config.json."
            )

        # Initialize Google Gemini client
        self.client = genai.Client(api_key=self.api_key)

    def generate(self, prompt: str, model: str = "gemini-2.5-flash") -> str:
        """
        Sends a text prompt to Gemini using the official Google SDK.
        """

        try:
            response = self.client.models.generate_content(
                model=model,
                contents=prompt
            )

            return response.text or ""

        except Exception as e:
            raise RuntimeError(f"Gemini SDK error: {e}")
