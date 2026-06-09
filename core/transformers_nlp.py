"""
Transformer NLP models via Hugging Face Inference API.
Uses cloud-based inference for summarization, classification, and masking.

All three tasks use raw requests to router.huggingface.co/hf-inference for
full payload control and consistent behaviour across model types.
"""
import requests
from typing import List, Dict, Any, Optional
from config import (
    HF_API_TOKEN,
    HF_SUMMARIZATION_MODEL, HF_CLASSIFICATION_MODEL, HF_MASKING_MODEL
)

_HF_BASE = "https://router.huggingface.co/hf-inference/models"


class TransformerModels:
    """Manages Hugging Face Inference API calls for NLP tasks."""

    def __init__(self):
        """Initialize transformer models API."""
        self.api_token = HF_API_TOKEN
        self.enabled = bool(self.api_token)
        self.timeout = 60

        if not self.api_token:
            print(
                "HF_API_TOKEN not set. Transformer commands are disabled. "
                "Set HF_API_TOKEN in your environment or .env file to enable them."
            )
        else:
            self._headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
            }

    def _post(self, model: str, payload: dict) -> Optional[Any]:
        """POST to HF inference router and return parsed JSON, or None on error.

        wait_for_model=True tells HF to block until the model is warm instead
        of immediately returning a 503 'currently loading' error.
        """
        payload.setdefault("options", {})["wait_for_model"] = True

        try:
            url = f"{_HF_BASE}/{model}"
            response = requests.post(url, headers=self._headers, json=payload, timeout=self.timeout)
            if not response.ok:
                print(f"Error calling {model} [{response.status_code}]: {response.text[:300]}")
                return None
            return response.json()
        except requests.exceptions.Timeout:
            print(f"Timeout calling {model} (model may still be loading, try again)")
            return None
        except Exception as e:
            print(f"Error calling {model}: {e}")
            return None

    def summarize(self, text: str, max_length: int = 130, min_length: int = 30) -> Optional[str]:
        """
        Summarize text using DistilBART (fast ~300MB, replaces bart-large-cnn which times out).

        Args:
            text: Text to summarize (minimum 50 words recommended)
            max_length: Maximum token length of summary
            min_length: Minimum token length of summary

        Returns:
            Summarized text or None if error
        """
        if len(text.split()) < 50:
            return "❌ Text too short. Please provide at least 50 words."
        if not self.enabled:
            return None

        result = self._post(HF_SUMMARIZATION_MODEL, {
            "inputs": text,
            "parameters": {
                "max_length": max_length,
                "min_length": min_length,
                "do_sample": False,
            },
        })

        if isinstance(result, list) and result:
            return result[0].get("summary_text")
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
        if not labels or len(labels) < 2 or not self.enabled:
            return None

        result = self._post(HF_CLASSIFICATION_MODEL, {
            "inputs": text,
            "parameters": {
                "candidate_labels": labels,
                "multi_label": multi_class,
            },
        })

        if not result or "labels" not in result:
            return None

        # API returns labels already sorted by score descending
        return {
            "text": text[:50] + "..." if len(text) > 50 else text,
            "labels": result["labels"],
            "scores": [round(s, 4) for s in result["scores"]],
            "top": f"{result['labels'][0]} ({result['scores'][0]:.2%})",
        }

    def fill_mask(self, text: str, top_k: int = 5) -> Optional[List[Dict[str, Any]]]:
        """
        Fill masked tokens in text (mask token: [MASK]).

        Args:
            text: Text with [MASK] token
            top_k: Number of top predictions

        Returns:
            List of predictions or None if error
        """
        if "[MASK]" not in text.upper() or not self.enabled:
            return None

        text = text.replace("[mask]", "[MASK]").replace("[Mask]", "[MASK]")

        result = self._post(HF_MASKING_MODEL, {
            "inputs": text,
            "parameters": {"top_k": top_k},
        })

        if not isinstance(result, list):
            return None

        return [
            {
                "token": r.get("token_str", "").strip(),
                "score": round(r.get("score", 0), 4),
                "sequence": r.get("sequence", ""),
            }
            for r in result[:top_k]
        ]


# Global transformer models instance
transformer_models = TransformerModels()
