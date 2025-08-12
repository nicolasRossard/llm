import requests
from typing import List
from application.ports.server_side.llm_client import LlmClient
from domain.schema.document_chunk import DocumentChunk

from litellm import completion



class LiteLlmClientAdapter(LlmClient):
    def __init__(self, model_name: str = "ollama/llama3.2:1b", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")

    def generate_answer(self, question: str, context_chunks: List[DocumentChunk]) -> str:
        context_text = "\n\n".join(chunk.text for chunk in context_chunks)
        prompt = self._build_prompt(question, context_text)

        response = completion(
            model=self.model_name,
            messages=[{"content": prompt, "role": "user"}],
            api_base=self.base_url,
            stream=False,
        )

        if response.status_code != 200:
            raise RuntimeError(f"Lite LLM call failed: {response.status_code} - {response.text}")

        result = response.json()
        return result.get("response", "pas de réponse").strip()

    def _build_prompt(self, question: str, context: str) -> str:
        return (
            "You are an intelligent assistant. Use the following context to answer the question. Say I don't know if you don't find element to answer to the question\n\n"
            f"Context:\n{context}\n\n"
            f"Question:\n{question}\n\n"
            "Answer:"
        )
