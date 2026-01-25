from client.llm_client import LLMClient
import asyncio

async def main() -> None:
    client = LLMClient()
    messages = [
        {"role": "user", "content": "what is your name?"}
    ]
    await client.chat_completion(messages=messages, stream=False)
    print("Done")

asyncio.run(main())