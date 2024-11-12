# src/services/llm.py
from typing import Dict
from anthropic import Anthropic
from openai import OpenAI
from src.config import settings, LLMProvider

class LLMService:
    def __init__(self):
        self.provider = settings.llm_provider
        if self.provider == LLMProvider.CLAUDE:
            self.client = Anthropic(api_key=settings.anthropic_api_key)
            self.model = settings.claude_model
        else:
            self.client = OpenAI(api_key=settings.openai_api_key)
            self.model = settings.gpt_model

    async def analyze_metrics(self, metrics: Dict, query: str) -> str:
        if self.provider == LLMProvider.CLAUDE:
            return await self._claude_analyze(metrics, query)
        return await self._gpt_analyze(metrics, query)

    async def _claude_analyze(self, metrics: Dict, query: str) -> str:
        response = await self.client.messages.create(
            model=self.model,
            messages=[{
                "role": "user",
                "content": f"Analyze these metrics: {metrics}\nQuery: {query}"
            }]
        )
        return response.content

    async def _gpt_analyze(self, metrics: Dict, query: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": f"Analyze these metrics: {metrics}\nQuery: {query}"}
            ]
        )
        return response.choices[0].message.content