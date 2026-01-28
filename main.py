from typing import Any
from client.llm_client import LLMClient
import asyncio
import click

class CLI:
    def __init__(self) -> None:
        pass
    
    def run_single(self):
        pass 
    
async def run(
        message: dict[str, Any]
):
    client = LLMClient()
    async for event in client.chat_completion(messages=message, stream=True): # type: ignore
        print(event)

@click.command()
@click.argument("prompt", required=False)
def main(
    prompt:str | None = None
) -> None:
    print(prompt)
    messages = [{"role": "user", "content": prompt}]
    asyncio.run(run(message=messages)) # type: ignore
    print("Done")
# lol
main()
