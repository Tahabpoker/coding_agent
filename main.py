from client.llm_client import LLMClient
import asyncio

async def main() -> None:
    client = LLMClient()
    messages = [
        {"role": "user", "content": "what is your name?"}
    ]
    async for event in client.chat_completion(messages=messages, stream=True):
        print(event)
    print("Done")

asyncio.run(main()) 