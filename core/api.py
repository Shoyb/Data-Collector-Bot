"""
API integration module for Data Collector Bot.
Handles external API calls (quotes, memes, etc.)
"""
import requests
import json
from typing import Optional, Dict, Any
from config import ZENQUOTES_API_URL, MEME_API_URL


class APIManager:
    """Manages external API integrations."""
    
    @staticmethod
    def get_random_quote() -> Optional[str]:
        """
        Fetch a random quote from ZenQuotes API.
        
        Returns:
            Formatted quote string or None if request fails
        """
        try:
            response = requests.get(ZENQUOTES_API_URL, timeout=5)
            response.raise_for_status()
            data = json.loads(response.text)
            if data and len(data) > 0:
                quote = data[0]['q']
                author = data[0]['a']
                return f"{quote}\n-{author}"
            return None
        except requests.RequestException as e:
            print(f"Error fetching quote: {e}")
            return None
    
    @staticmethod
    def get_random_meme() -> Optional[Dict[str, Any]]:
        """
        Fetch a random meme from meme API.
        
        Returns:
            Dictionary with meme data or None if request fails
        """
        try:
            response = requests.get(MEME_API_URL, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching meme: {e}")
            return None


# Global API manager instance
api_manager = APIManager()
