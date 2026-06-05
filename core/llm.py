"""
LLM (Large Language Model) management module for Data Collector Bot.
Handles llama.cpp server and Qwen inference.
"""
import subprocess
import requests
import time
import re
import asyncio
from typing import Optional, Tuple, Dict, Any
from config import (
    LLM_SERVER_URL, LLM_MAX_TOKENS, LLM_TEMPERATURE, LLM_TIMEOUT,
    LLM_MAX_THINKING_TOKENS, LLM_REPEAT_PENALTY, LLM_MODEL_PATH,
    LLM_SERVER_PATH
)


class LLMManager:
    """Manages LLM server and inference."""
    
    def __init__(self):
        """Initialize LLM manager."""
        self.llama_process = None
        self.system_prompt = """You are a fast, concise assistant. Follow these rules strictly:
- Answer directly without long preambles
- Be brief and to the point
- Do not over-explain unless asked
- /no_think"""
    
    def start_server(self) -> bool:
        """
        Start llama.cpp server.
        
        Returns:
            True if server started successfully
        """
        print("🚀 Starting llama.cpp server...")
        try:
            self.llama_process = subprocess.Popen(
                [
                    LLM_SERVER_PATH,
                    "--model", LLM_MODEL_PATH,
                    "--port", "8080",
                    "--threads", "6",
                    "--temp", "0.3"
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print(f"   Server PID: {self.llama_process.pid}")
            return self.wait_for_server()
        except Exception as e:
            print(f"Error starting server: {e}")
            return False
    
    def wait_for_server(self, retries: int = 20, delay: int = 2) -> bool:
        """
        Wait for server to be ready.
        
        Args:
            retries: Number of retry attempts
            delay: Delay between retries in seconds
            
        Returns:
            True if server is ready, False otherwise
        """
        print("Waiting for server to be ready", end="", flush=True)
        for _ in range(retries):
            try:
                r = requests.get("http://127.0.0.1:8080/health", timeout=2)
                if r.status_code == 200:
                    print(" ready")
                    return True
            except Exception:
                pass
            print(".", end="", flush=True)
            time.sleep(delay)
        print(" failed")
        return False
    
    def stop_server(self):
        """Stop llama.cpp server."""
        if self.llama_process:
            print("Stopping llama.cpp server...")
            self.llama_process.terminate()
            self.llama_process.wait()
            print("   Server stopped.")
    
    def ask_qwen(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Tuple[str, str, Dict[str, Any]]:
        """
        Query Qwen model.
        
        Args:
            prompt: User prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Tuple of (answer, reasoning, stats)
        """
        data = {
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature if temperature is not None else LLM_TEMPERATURE,
            "max_tokens": max_tokens if max_tokens is not None else LLM_MAX_TOKENS,
            "repeat_penalty": LLM_REPEAT_PENALTY,
            "stream": False,
        }

        if LLM_MAX_THINKING_TOKENS > 0:
            data["thinking"] = {
                "type": "enabled",
                "budget_tokens": LLM_MAX_THINKING_TOKENS
            }

        start = time.time()
        try:
            r = requests.post(LLM_SERVER_URL, json=data, timeout=LLM_TIMEOUT)
            r.raise_for_status()
            elapsed = time.time() - start

            result = r.json()
            message = result["choices"][0]["message"]
            timings = result.get("timings", {})
            usage = result.get("usage", {})

            content = message.get("content", "").strip()
            reasoning = message.get("reasoning_content", "").strip()
            answer = content if content else reasoning

            stats = {
                "elapsed": elapsed,
                "prompt_tokens": usage.get("prompt_tokens", "?"),
                "completion_tokens": usage.get("completion_tokens", "?"),
                "total_tokens": usage.get("total_tokens", "?"),
                "tok_per_sec": round(timings.get("predicted_per_second", 0), 2),
                "finish_reason": result["choices"][0].get("finish_reason", "?"),
                "max_tokens_used": max_tokens if max_tokens is not None else LLM_MAX_TOKENS,
                "temp_used": temperature if temperature is not None else LLM_TEMPERATURE,
            }

            return answer, reasoning, stats
        except Exception as e:
            raise e
    
    @staticmethod
    def parse_args(raw: str) -> Tuple[str, Optional[int], Optional[float]]:
        """
        Parse optional --tokens and --temp flags.
        
        Args:
            raw: Raw command string
            
        Returns:
            Tuple of (cleaned_prompt, max_tokens, temperature)
        """
        max_tokens = None
        temperature = None

        token_match = re.search(r"--tokens\s+(\d+)", raw)
        temp_match = re.search(r"--temp\s+([0-9.]+)", raw)

        if token_match:
            max_tokens = int(token_match.group(1))
            raw = raw.replace(token_match.group(0), "")
        if temp_match:
            temperature = float(temp_match.group(1))
            raw = raw.replace(temp_match.group(0), "")

        return raw.strip(), max_tokens, temperature


# Global LLM manager instance
llm_manager = LLMManager()
