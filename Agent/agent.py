from __future__ import annotations
from typing import AsyncGenerator
from Agent.events import AgentEvent, AgentEventType
from client.llm_client import LLMClient
from client.response import StreamEventType


class Agent:
    """
    Agent responsible for orchestrating the interaction between the user
    and the LLM client.

    This class:
    - Emits high-level AgentEvents
    - Streams responses from the LLM
    - Converts low-level stream events into agent-level events
    - Manages lifecycle of the LLM client
    """

    def __init__(self) -> None:
        """
        Initialize the Agent.

        Creates an instance of LLMClient that will be used
        to communicate with the underlying language model.
        """
        self.client = LLMClient()

    async def run(self, message: str):
        """
        Entry point for executing the agent workflow.

        Parameters:
        -----------
        message : str
            The user input message to process.

        Yields:
        -------
        AgentEvent
            Stream of AgentEvents representing:
            - Agent start
            - Streaming text deltas
            - Completion
            - Agent end
        """

        # Emit event indicating the agent has started processing
        yield AgentEvent.agent_start(message=message)

        # NOTE:
        # Intended place to add the user message to conversation context.
        # Currently not implemented.
        # Execute the internal agent loop and forward events
        final_response: str | None = None
        async for event in self._agentic_loop():
            yield event
            # Capture the final response once full text is complete
            if event.type == AgentEventType.TEXT_COMPLETE:
                final_response = event.data.get("content")

        # Emit final agent end event with the complete response
        yield AgentEvent.agent_end(final_response)  # type: ignore

    async def _agentic_loop(self) -> AsyncGenerator[AgentEvent, None]:
        """
        Core internal loop responsible for:

        - Sending messages to the LLM client
        - Streaming partial responses
        - Emitting structured AgentEvents

        Returns:
        --------
        AsyncGenerator[AgentEvent, None]
            Yields AgentEvent objects during the streaming lifecycle.
        """

        # Hardcoded user message (placeholder for dynamic context handling)
        messages = [{"role": "user", "content": "hey what is going on"}]

        # Accumulator for building the complete response from streamed chunks
        response_text = ""

        # Stream completion from the LLM client
        async for event in self.client.chat_completion(messages=messages, stream=True):  # type: ignore

            # Handle incremental text tokens
            if event.type == StreamEventType.TEXT_DELTA:
                if event.text_delta:
                    content = event.text_delta.content  # type: ignore

                    # Append incoming token to full response buffer
                    response_text += content

                    # Emit partial text to consumers
                    yield AgentEvent.text_delta(content=content)

            # Handle streaming error events
            elif event.type == StreamEventType.ERROR:
                yield AgentEvent.agent_error(
                    event.error or "unknown error occured",
                )  # type: ignore

        # After streaming completes, emit full response event
        if response_text:
            yield AgentEvent.text_complete(response_text)  # type: ignore
 
    async def __aenter__(self) -> Agent:
        """
        Async context manager entry.

        Allows usage:
            async with Agent() as agent:
                ...
        """
        return self

    async def __aexit__(
            self, 
            exc_type, 
            exc_val, 
            exc_tb,
    ) -> None:
        """
        Async context manager exit.

        Ensures that the LLM client connection is properly closed
        and resources are released.
        """
        if self.client:
            await self.client.close()
            self.client = None
