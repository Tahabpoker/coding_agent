import asyncio
import sys
import click

from typing import Any
from Agent.agent import Agent
from Agent.events import AgentEventType
from ui.tui import TUI, get_console

# Obtain a shared console instance for TUI rendering.
console = get_console()

class CLI:

    def __init__(self) -> None:
        # Initially there is no Agent; it is created when run_single is invoked.
        self.agent: Agent | None = None
        self.tui = TUI(console)
    
    async def run_single(self, message: str) -> str | None:
       
        async with Agent() as agent:
            self.agent = agent
            # Delegate to the internal processor that streams events.
            return await self._process_message(message) # type: ignore
    
    async def _process_message(self, message: str)-> str | None:
        
        if not self.agent:
            # No agent available to handle the message.
            return None
        # The agent yields events asynchronously; iterate and handle relevant ones.
        async for event in self.agent.run(message=message):
            if event.type == AgentEventType.TEXT_DELTA:
                # Extract partial content safely and stream to the TUI.
                content = event.data.get("content", "")
                self.tui.stream_assistant_delta(content=content)

# CLI entrypoint using click.
@click.command()
@click.argument("prompt", required=False)
def main(
    prompt:str | None = None
):
    print(f"starting program")
    cli = CLI()
    # Echo the prompt (kept from original behavior).
    print(prompt)
     # messages = [{"role": "user", "content": prompt}]
    # If a prompt was provided, run the agent synchronously via asyncio.run.
    if prompt:
        result = asyncio.run(cli.run_single(prompt))
        if result is None:
            # Non-zero exit code indicates a processing failure.
            sys.exit(1)
    print(f"program end")

# Invoke the click command when the module is executed.
main()
