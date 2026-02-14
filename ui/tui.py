from rich.console import Console
from rich.theme import Theme

AGENT_THEME = Theme(
    {
        # Core messaging
        "info": "dim cyan",
        "warning": "bold yellow",
        "error": "bright_red bold",
        "success": "bold green",
        "dim": "dim",
        "muted": "grey50",
        "border": "grey37",
        "highlight": "bold cyan",
        
        # Roles with enhanced styling
        "user": "bright_blue bold",
        # "user.label": "bright_blue",
        "assistant": "bright_white",
        # "assistant.label": "bright_white dim",
        
        # Tools with consistent hierarchy
        "tool": "bright_magenta bold",
        "tool.read": "cyan bold",
        "tool.write": "bright_yellow bold",
        "tool.shell": "magenta bold",
        "tool.network": "bright_blue bold",
        "tool.memory": "green bold",
        "tool.mcp": "bright_cyan bold",
        
        # Code blocks and syntax
        "code": "white",
        "code.bracket": "grey66",
        "code.string": "bright_green",
        "code.keyword": "bright_magenta",
        
        # Status indicators
        "status.pending": "yellow dim",
        "status.running": "cyan bold",
        "status.completed": "green bold",
        "status.failed": "bright_red",
        
        # Highlights and emphasis
        "highlight": "bold cyan",
        #Roles
        "user": "bright_blue bold",
        "user.label": "bright_blue",
        "assistant": "bright_white",
        "assistant.label": "bright_white dim",
        
        # Tools with consistent hierarchy
        "tool": "bright_magenta bold",
        "tool.read": "cyan bold",
        "tool.write": "bright_yellow bold",
        "tool.shell": "magenta bold",
        "tool.network": "bright_blue bold",
        "tool.memory": "green bold",
        "tool.mcp": "bright_cyan bold",
        
        # Code blocks and syntax
        "code": "white",
        "code.bracket": "grey66",
        "code.string": "bright_green",
        "code.keyword": "bright_magenta",
        
        # Status indicators
        "status.pending": "yellow dim",
        "status.running": "cyan bold",
        "status.completed": "green bold",
        "status.failed": "bright_red",
        
        # Highlights and emphasis
        "highlight": "bold cyan",
        "emphasis": "bold white",
        "accent": "bright_cyan",
    }
)
# Centralized console instance for the TUI, initialized with the AGENT_THEME.
_console: Console  | None = None
def get_console() ->Console:
    global _console
    if _console is None:
        _console = Console(theme=AGENT_THEME, highlight=False) 
    return _console
# TUI class responsible for rendering output to the console, utilizing the centralized console instance with the defined theme.
class TUI:
    def __init__(
            self,
            _console: Console | None = None
    ) -> None:

        self.console = _console or get_console()
    
    def stream_assistant_delta(self, content: str) -> None:
        self.console.print(content, end = "", markup=False)
        