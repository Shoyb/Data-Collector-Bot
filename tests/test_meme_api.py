"""
Test script for meme API integration.
"""
import requests
import json
from core.api import api_manager


def test_meme_api():
    """Test fetching a random meme."""
    print("Testing meme API...")
    meme = api_manager.get_random_meme()
    if meme:
        print("Meme API works!")
        print(json.dumps(meme, indent=2))
    else:
        print("Failed to fetch meme")


if __name__ == "__main__":
    test_meme_api()
