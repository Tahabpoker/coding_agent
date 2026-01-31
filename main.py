import asyncio
import click
from typing import Any
from Agent.agent import Agent
from Agent.events import AgentEventType

class CLI:
    def __init__(self) -> None:
        self.agent: Agent | None = None
    
    def run_single(self, message):
        async with Agent() as agent:
            self.agent = agent
            self._process_message(message) # type: ignore
    async def _process_message(self, message: str)-> str | None:
        if not self.agent:
            return None
        async for event in self.agent.run(message=message):
            if event.type == AgentEventType.TEXT_DELTA:
                content = event.data.get("content", "")


@click.command()
@click.argument("prompt", required=False)
def main(
    prompt:str | None = None
):
    cli = CLI()
    print(prompt)
    # messages = [{"role": "user", "content": prompt}]
    if prompt:
        async.run(cli.run_single(prompt))

main()
