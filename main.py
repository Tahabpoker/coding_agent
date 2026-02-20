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
        
        assistant_streaming = False
        final_response: str | None = None
        # The agent yields events asynchronously; iterate and handle relevant ones.
        async for event in self.agent.run(message=message):
            if event.type == AgentEventType.TEXT_DELTA:
                # Extract partial content safely and stream to the TUI.
                content = event.data.get("content", "")
                if not assistant_streaming:
                    self.tui.begin_assistant()
                    assistant_streaming = True
                self.tui.stream_assistant_delta(content=content)
            elif event.type == AgentEventType.TEXT_COMPLETE:
                final_response = event.data.get("content", "")
                if assistant_streaming:
                    assistant_streaming = False
                    self.tui.end_assistant()
            elif event.type == AgentEventType.AGENT_ERROR:
                error = event.data.get("error", "unknown error")
                # console.print(error, style="error") # use this when markup is disabled in tui.py: _console
                console.print(f"\n[error]Error: {error}[/error]")    
        return final_response # type: ignore

# CLI entrypoint using click.
@click.command()
@click.argument("prompt", required=False)
def main(
    prompt:str | None = None
):
    # print(f"starting program") # debug statements
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
    # print(f"program end") # debug statements

# Invoke the click command when the module is executed.
main()

# changes to branch refactor/random will be push and merged to refactor/main for testing purposes