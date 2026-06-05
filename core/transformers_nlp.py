"""
Transformer NLP models via Hugging Face Inference API.
Uses cloud-based inference for summarization, classification, and masking.
"""
import requests
from typing import List, Dict, Any, Optional
from config import (
    HF_API_TOKEN, HF_API_URL,
    HF_SUMMARIZATION_MODEL, HF_CLASSIFICATION_MODEL, HF_MASKING_MODEL
)


class TransformerModels:
    """Manages Hugging Face Inference API calls for NLP tasks."""
    
    def __init__(self):
        """Initialize transformer models API."""
        self.api_token = HF_API_TOKEN
        self.enabled = bool(self.api_token)
        self.headers = {"Authorization": f"Bearer {self.api_token}"} if self.enabled else {}
        self.timeout = 30
        if not self.enabled:
            print(
                "HF_API_TOKEN not set. Transformer commands are disabled. "
                "Set HF_API_TOKEN in your environment or .env file to enable them."
            )

    def _call_api(self, model: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Call Hugging Face Inference API.
        
        Args:
            model: Model name/ID
            payload: Request payload
        
        Returns:
            API response or None if error
        """
        if not self.enabled:
            print(f"HF_API_TOKEN not set. Cannot call model: {model}")
            return None

        try:
            url = f"{HF_API_URL}/{model}"
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            print(f"API timeout for {model}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"API error for {model}: {e}")
            return None
    
    def summarize(self, text: str, max_length: int = 150, min_length: int = 50) -> Optional[str]:
        """
        Summarize text using BART model on HF cloud.
        
        Args:
            text: Text to summarize (minimum 50 tokens recommended)
            max_length: Maximum length of summary
            min_length: Minimum length of summary
            
        Returns:
            Summarized text or None if error
        """
        try:
            if len(text.split()) < 50:
                return "❌ Text too short. Please provide at least 50 words."
            
            payload = {
                "inputs": text,
                "parameters": {
                    "max_length": max_length,
                    "min_length": min_length,
                    "do_sample": False
                }
            }
            
            result = self._call_api(HF_SUMMARIZATION_MODEL, payload)
            if result and len(result) > 0:
                return result[0].get('summary_text', None)
            return None
        except Exception as e:
            print(f"Error summarizing: {e}")
            return None
    
    def zero_shot_classify(
        self,
        text: str,
        labels: List[str],
        multi_class: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Classify text into one of given labels (zero-shot).
        
        Args:
            text: Text to classify
            labels: List of possible labels
            multi_class: Allow multiple label predictions
            
        Returns:
            Dictionary with scores and labels or None if error
        """
        try:
            if not labels or len(labels) < 2:
                return None
            
            payload = {
                "inputs": text,
                "parameters": {
                    "candidate_labels": labels,
                    "multi_class": multi_class
                }
            }
            
            result = self._call_api(HF_CLASSIFICATION_MODEL, payload)
            
            if result:
                return {
                    "text": text[:50] + "..." if len(text) > 50 else text,
                    "labels": result.get('labels', []),
                    "scores": [round(s, 4) for s in result.get('scores', [])],
                    "top": f"{result.get('labels', [''])[0]} ({result.get('scores', [0])[0]:.2%})"
                }
            return None
        except Exception as e:
            print(f"Error classifying: {e}")
            return None
    
    def fill_mask(self, text: str, top_k: int = 5) -> Optional[List[Dict[str, Any]]]:
        """
        Fill masked tokens in text (mask token: [MASK]).
        
        Args:
            text: Text with [MASK] token
            top_k: Number of top predictions
            
        Returns:
            List of predictions or None if error
        """
        try:
            if "[MASK]" not in text.upper():
                return None
            
            # Ensure MASK is uppercase for BERT
            text = text.replace('[mask]', '[MASK]').replace('[Mask]', '[MASK]')
            
            payload = {
                "inputs": text,
                "parameters": {
                    "top_k": top_k
                }
            }
            
            results = self._call_api(HF_MASKING_MODEL, payload)
            
            if results and isinstance(results, list):
                return [
                    {
                        "token": r.get('token_str', '').strip(),
                        "score": round(r.get('score', 0), 4),
                        "sequence": r.get('sequence', '')
                    }
                    for r in results[:top_k]
                ]
            return None
        except Exception as e:
            print(f"Error filling mask: {e}")
            return None


# Global transformer models instance
transformer_models = TransformerModels()

