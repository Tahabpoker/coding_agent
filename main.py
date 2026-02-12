# ...existing code...
"""
main.py
-------

Simple CLI entrypoint for the coding_agent application.

Responsibilities:
- Parse a single optional prompt argument from the command line (click).
- Create and manage an Agent instance to process the prompt.
- Stream assistant text deltas to the TUI.

No runtime logic changes were made; this file only adds docstrings and inline comments
to help maintainers understand the control flow.
"""
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
    """Command-line helper that coordinates Agent and TUI for a single prompt.

    Attributes:
        agent: The active Agent instance while processing a message (or None).
        tui: The TUI instance used to stream assistant output.
    """
    def __init__(self) -> None:
        # Initially there is no Agent; it is created when run_single is invoked.
        self.agent: Agent | None = None
        self.tui = TUI(console)
    
    async def run_single(self, message: str) -> str | None:
        """Run the agent once for the provided message.

        Creates the Agent as an async context manager so resources are properly
        initialized and cleaned up. The Agent instance is stored on self so
        _process_message can access it.

        Returns:
            The result string from processing, or None on failure.
        """
        async with Agent() as agent:
            self.agent = agent
            # Delegate to the internal processor that streams events.
            return await self._process_message(message) # type: ignore
    
    async def _process_message(self, message: str)-> str | None:
        """Process a message by consuming events from Agent.run and streaming to TUI.

        The Agent produces events; we only handle TEXT_DELTA events here and
        stream their 'content' field to the TUI. If there's no active agent,
        return None to indicate failure.
        """
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
    """Entry point called when running the script.

    If a prompt argument is provided, run the agent once and exit with a non-zero
    status on failure.
    """
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

# Invoke the click command when the module is executed.
main()
# ...existing code...