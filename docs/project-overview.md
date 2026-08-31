# Project Overview

## 1. Purpose and Scope

This repository is an **experimental terminal AI coding agent** written in Python. Its goal is to let a user interact with a large language model through a CLI/TUI interface, while giving the model access to a controlled set of tools such as file reading, editing, shell execution, web access, todos, and custom integrations.

At a high level, the project combines four ideas:

- **Conversational interaction** through a command-line interface.
- **Tool-augmented reasoning**, where the model can call functions instead of only generating text.
- **Safety and control**, using approval policies, hooks, and path-aware checks.
- **Extensibility**, through built-in tools, dynamically discovered tools, MCP servers, and subagents.

The codebase is still early-stage. The short `README.md` explicitly says the project is under construction, so the implementation should be read as a working architecture rather than a finished product.

## 2. Theoretical Background

This project follows an **agentic loop** pattern:

1. The user sends a request.
2. The system builds a prompt from the system instructions, session history, and tool definitions.
3. The LLM streams back either plain text, tool calls, or both.
4. Tool calls are executed locally.
5. Tool results are added back into the conversation.
6. The loop continues until the model stops requesting tools and returns a final answer.

Important concepts used in this repository:

- **LLM function calling**: tools are exposed as JSON schemas so the model can request structured actions.
- **Context management**: prior messages are stored and sometimes compacted or pruned to fit the model context window.
- **Streaming**: assistant text is printed incrementally while the response is generated.
- **Approval policies**: mutating or dangerous operations can be auto-approved, rejected, or confirmed interactively.
- **MCP (Model Context Protocol)**: external tool servers can be connected and exposed like local tools.
- **Subagents**: specialized nested agents can be launched with restricted tool access for focused tasks.

## 3. Technology Stack

The main technologies and libraries are:

- **Python** for the implementation language.
- **`click`** for CLI argument parsing in `main.py`.
- **`rich`** for terminal UI rendering in `ui/tui.py`.
- **`pydantic`** for configuration and tool parameter schemas.
- **`openai`** async client for chat completions in `client/llm_client.py`.
- **`platformdirs`** for user config/data directories.
- **`tomli`** for reading TOML configuration files.

## 4. Project Structure

The repository is organized around the runtime lifecycle of the agent.

### 4.1 Entry Point and UI

- `main.py`
  Handles CLI startup, interactive mode, one-shot mode, slash commands, session save/resume, and top-level config validation.
- `ui/tui.py`
  Renders assistant output, tool calls, diffs, confirmations, and formatted panels using Rich.

### 4.2 Agent Core

- `Agent/agent.py`
  Contains the main agent loop. It streams model output, collects tool calls, invokes tools, detects loops, and manages compression.
- `Agent/session.py`
  Wires together all subsystems: LLM client, registry, approval manager, hook system, MCP manager, tool discovery, context manager, and persistence-related state.
- `Agent/events.py`
  Defines the event types passed from the agent to the UI.

### 4.3 Model and Response Handling

- `client/llm_client.py`
  Wraps the async OpenAI-compatible client and converts streaming chunks into internal event objects.
- `client/response.py`
  Defines response dataclasses like `StreamEvent`, `ToolCall`, and `TokenUsage`.

### 4.4 Configuration and Prompting

- `config/config.py`
  Defines the main `Config` model, approval policies, hook config, shell environment policy, and MCP server config.
- `config/loader.py`
  Loads and merges system config, project config, and local project instructions.
- `prompts/system.py`
  Builds the system prompt that drives the model's operating rules.

### 4.5 Context and Conversation State

- `context/manager.py`
  Stores chat messages, token usage, system prompt, summary replacement, and tool output pruning.
- `context/compaction.py`
  Summarizes long sessions into a continuation prompt when the context window becomes too large.
- `context/loop_detector.py`
  Detects repeated tool-call or response cycles.

### 4.6 Tools and Extensibility

- `tools/base.py`
  Defines the abstract tool model, result type, diffs, and confirmation metadata.
- `tools/registry.py`
  Registers tools, filters by allowed tools, validates arguments, runs approval checks, fires hooks, and invokes implementations.
- `tools/builtin/`
  Contains built-in tools such as `read_file`, `edit`, `write_file`, `shell`, `grep`, `glob`, `web_fetch`, `web_search`, `todo`, and `memory`.
- `tools/discovery.py`
  Dynamically discovers Python tool files from `.ai-agent/tools`.
- `tools/subagents.py`
  Defines nested subagent tools such as a codebase investigator and code reviewer.
- `tools/mcp/`
  Connects external MCP servers and registers their tools in the same registry.

### 4.7 Safety, Hooks, and Utilities

- `safety/approval.py`
  Encodes approval decisions and command-safety heuristics.
- `hooks/hook_system.py`
  Runs commands before or after agent/tool execution.
- `utils/`
  Holds small helpers for paths, text handling, and errors.

## 5. End-to-End Runtime Flow

The main request path is:

1. `main.py` loads configuration with `load_config()`.
2. `CLI.run_interactive()` or `CLI.run_single()` creates an `Agent`.
3. `Agent.__aenter__()` initializes a `Session`.
4. `Session.initialize()`:
   - starts MCP,
   - registers MCP tools,
   - discovers local custom tools,
   - loads user memory,
   - constructs the `ContextManager`.
5. `Agent.run()` adds the user message to context and starts `_agentic_loop()`.
6. `_agentic_loop()` sends messages and tool schemas to the LLM client.
7. The LLM streams text and tool call requests.
8. Tool calls are validated and executed through `ToolRegistry.invoke()`.
9. Tool results are inserted into context as `tool` messages.
10. The loop continues until there are no more tool calls.

The control flow in `Agent/agent.py` is the center of the project:

```python
async def _agentic_loop(self) -> AsyncGenerator[AgentEvent, None]:
    max_turns = self.config.max_turns

    for turn_num in range(max_turns):
        self.session.increment_turn()

        if self.session.context_manager.needs_compression():
            summary, usage = await self.session.chat_compactor.compress(
                self.session.context_manager
            )

            if summary:
                self.session.context_manager.replace_with_summary(summary)

        tool_schemas = self.session.tool_registry.get_schemas()

        async for event in self.session.client.chat_completion(
            self.session.context_manager.get_messages(),
            tools=tool_schemas if tool_schemas else None,
        ):
            ...
```

Why this matters:

- The agent is **iterative**, not single-shot.
- Tool calling is a **first-class runtime behavior**, not an afterthought.
- Context compaction is integrated into the loop instead of being handled externally.

## 6. Key Features and How They Work

### 6.1 Built-In Tools

Built-in tools are registered in `tools/builtin/__init__.py` and instantiated by `create_default_registry()` in `tools/registry.py`.

The base abstraction is intentionally small:

```python
class Tool(abc.ABC):
    name: str = "base_tool"
    description: str = "Base tool"
    kind: ToolKind = ToolKind.READ

    @property
    def schema(self) -> dict[str, Any] | type["BaseModel"]:
        raise NotImplementedError

    @abc.abstractmethod
    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        pass
```

Best practices visible here:

- Tools declare a **schema** for validation.
- Tools return a structured **`ToolResult`** rather than raw strings.
- Mutating behavior is categorized by **`ToolKind`**, which makes approval decisions easier.

### 6.2 Tool Validation, Approval, and Execution

The tool registry centralizes execution policy:

```python
validation_errors = tool.validate_params(params)
if validation_errors:
    return ToolResult.error_result(...)

await hook_system.trigger_before_tool(name, params)

if approval_manager:
    confirmation = await tool.get_confirmation(invocation)
    ...
    decision = await approval_manager.check_approval(context)

result = await tool.execute(invocation)
await hook_system.trigger_after_tool(name, params, result)
```

This is a strong design choice because it keeps common concerns out of each tool implementation:

- validation,
- safety review,
- confirmation,
- hook execution,
- error wrapping.

### 6.3 Context Management

The conversation state is stored in `ContextManager`, which builds the message list sent to the LLM.

```python
def get_messages(self) -> list[dict[str, Any]]:
    messages = []

    if self._system_prompt:
        messages.append({"role": "system", "content": self._system_prompt})

    for item in self._messages:
        messages.append(item.to_dict())

    return messages
```

This keeps the agent state model simple and transparent. The same module also handles:

- token accounting,
- tool-result pruning,
- summary replacement after compaction,
- session clearing.

### 6.4 Context Compaction

When usage crosses 80% of the configured context window, the project summarizes previous conversation history and replaces the in-memory thread with a structured continuation prompt.

This is a practical strategy for long-running sessions because it trades exact transcript fidelity for continued usability.

### 6.5 Loop Detection

`context/loop_detector.py` records repeated actions and detects exact repeats or short cycles. When a loop is found, a loop-breaker prompt is injected as a new user message. This is a lightweight but useful guardrail for tool-using agents.

### 6.6 Hooks

Hooks let maintainers run external commands before or after agent or tool execution. This can be used for logging, auditing, or custom automation.

### 6.7 Persistence

`Agent/persistence.py` stores sessions and checkpoints as JSON snapshots. The CLI exposes commands like `/save`, `/sessions`, `/resume`, `/checkpoint`, and `/restore`.

### 6.8 MCP and Subagents

The project supports two extension models:

- **MCP servers** for external tool providers.
- **Subagents** for specialized nested reasoning with restricted tool sets.

This is one of the more interesting parts of the architecture because it shows the project is designed to scale beyond a single monolithic tool list.

## 7. Representative Code Walkthrough

The `read_file` tool is a good example of the house style:

```python
class ReadFileTool(Tool):
    name = "read_file"
    kind = ToolKind.READ
    schema = ReadFileParams

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        params = ReadFileParams(**invocation.params)
        path = resolve_path(invocation.cwd, params.path)

        if not path.exists():
            return ToolResult.error_result(f"File not found: {path}")

        content = path.read_text(encoding="utf-8")
        ...
        return ToolResult.success_result(output=output, metadata={...})
```

What this snippet demonstrates:

- Parameter parsing uses **Pydantic**.
- Filesystem work is isolated in the tool.
- Errors are returned in a structured way.
- Output includes metadata for the UI and higher-level agent logic.

This pattern is repeated across most built-in tools and is a good reference if new tools are added later.

## 8. Example Use Case

### Scenario

- **Input**: the user asks, "Read `main.py` and explain how interactive mode works."
- **Expected behavior**:
  1. The agent sends the request and available tool schemas to the model.
  2. The model chooses `read_file` for `main.py`.
  3. The tool returns line-numbered file content.
  4. The result is appended to the conversation.
  5. The model produces a natural-language explanation of `CLI.run_interactive()` and related command handling.
- **Output**: the user sees a streamed explanation in the TUI, along with a visible tool call panel showing that `read_file` was used.

This example captures the core value of the system: the model is not guessing blindly. It can inspect local code before answering.

## 9. Coding Style and Implementation Patterns

The project shows several consistent implementation patterns:

- **Dataclasses** for internal transport/event objects.
- **Pydantic models** for configuration and input validation.
- **Async I/O** for model calls and shell/process work.
- **Registry-based extensibility** for tools.
- **Small focused modules** rather than a single large runtime file.

Good practices worth preserving:

- Centralized tool execution logic in the registry.
- Explicit event types between the agent and UI.
- Structured tool results with metadata and diffs.
- Clear separation between config loading, agent loop, UI, and tools.

## 10. Review Notes and Risks

This section is important if the document is also used for future review work.

- **Case-sensitive import risk**: imports use `agent.*` while the directory is `Agent/`, which may fail on case-sensitive systems.
- **Approval policy typo**: `AUTO_EDIT` is assigned the string `"auto-edut"` in `config/config.py`.
- **Broken temperature setter**: `temperature` is attached to the wrong property setter decorator.
- **Config error flow bug**: `main.py` can use `config` even after config loading fails.
- **Restore command bugs**: `/restore` has a typo in the help text and references `checkpoint_id` incorrectly.
- **Tool kind null handling bug**: `_get_tool_kind()` can dereference `None`.
- **TUI robustness risk**: read-file output parsing appears to assume a helper never returns `None`.
- **Instruction file mismatch**: loader reads `AGENT.MD` while prompts refer to `AGENTS.md`.
- **Path/scope risk**: read operations appear able to use absolute paths outside the workspace.
- **Sample config drift**: `.ai-agent/config.toml` contains machine-specific and likely stale examples.

These are useful review targets because they affect portability, safety, and operator confidence.

## 11. Summary

This project is a promising **tool-using terminal coding agent** with a clear architectural direction:

- a structured async agent loop,
- a reusable tool interface,
- explicit safety and approval controls,
- context scaling features,
- and multiple extension mechanisms.

For a reviewer or future maintainer, the most important files to understand first are:

1. `main.py`
2. `Agent/agent.py`
3. `Agent/session.py`
4. `tools/registry.py`
5. `context/manager.py`
6. `client/llm_client.py`

Together, these files explain most of the runtime behavior of the system.
