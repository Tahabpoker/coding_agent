import asyncio
from typing import AsyncGenerator
from typing import Any
from openai import APIConnectionError, APIError, AsyncOpenAI, RateLimitError
from dotenv import load_dotenv
import os

from client.response import EventType, StreamEvent, TextDelta, TokenUsage
load_dotenv()

API_KEY = os.getenv("API_KEY")

class LLMClient:
    def __init__(self) -> None:
        self._client : AsyncOpenAI | None = None
        self._max_retries: int = 3

    def get_client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=API_KEY,
                base_url="https://openrouter.ai/api/v1"
            )
        return self._client
    
    async def close(self) -> None:
        if self._client:
            await self._client.close()
            self._client = None 


    async def chat_completion(
            self,
            messages: list[dict[str, Any]], 
            stream: bool = True
    )-> AsyncGenerator[StreamEvent, None]:
        
            

    async def _stream_response(self, 
                               client: AsyncOpenAI, 
                               kwargs: dict[str, Any]
    ) -> AsyncGenerator[StreamEvent, None]: 
        response = await client.chat.completions.create(**kwargs)
        finish_reason: str | None = None
        usage: TokenUsage | None = None  

        async for chunk in response:
            if hasattr(chunk, "usage") and chunk.usage:
                usage = TokenUsage(
                    prompt_tokens = chunk.usage.prompt_tokens,
                    completion_tokens = chunk.usage.completion_tokens,
                    total_tokens = chunk.usage.total_tokens,
                    cached_tokens= chunk.usage.prompt_tokens_details.cached_tokens,
                )
            if not chunk.choices:
                continue
            
            choice = chunk.choices[0]
            delta = choice.delta
            if choice.finish_reason:
                finish_reason = choice.finish_reason

            if delta.content:
                yield StreamEvent(
                    type=EventType.TEXT_DELTA,
                    text_delta=TextDelta(delta.content)
                )
        yield StreamEvent(
            type=EventType.MESSAGE_COMPLETE,
            finish_reason=finish_reason,
            usage=usage,
        )
    async def _non_stream_response(self, 
                                   client: AsyncOpenAI, 
                                   kwargs: dict[str, Any]
    ) -> StreamEvent:
        response = await client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        message = choice.message 
        text_delta = None
        if message.content:
            text_delta =  TextDelta(content=message.content)
        usage = None        
        if response.usage:
            usage = TokenUsage(
                prompt_tokens = response.usage.prompt_tokens,
                completion_tokens = response.usage.completion_tokens,
                total_tokens = response.usage.total_tokens,
                cached_tokens= response.usage.prompt_tokens_details.cached_tokens,
            )

        return StreamEvent(
            type=EventType.MESSAGE_COMPLETE,
            text_delta=text_delta,
            finish_reason=choice.finish_reason,
            usage=usage
        )