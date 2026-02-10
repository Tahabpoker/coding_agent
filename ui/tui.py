from rich.console import Console
from rich.theme import Theme

AGENT_THEME = Theme(
    {
        "info": "dim cyan",
        "warning": "yellow",
        "error": "bright_red bold",
        "success": "green",
        "dim": "dim",
        "muted": "grey50",
        "border": "grey37",
<<<<<<< Updated upstream
=======
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
>>>>>>> Stashed changes
        "highlight": "bold cyan",
        #Roles
        "user": "bright_blue bold",
        "assistant": "bright_white",
        # Tools
        "tool": "bright_magenta bold",
        "tool.read": "cyan",
        "tool.write": "bright_yellow",
        "tool.shell": "magenta",
        "tool.network": "bright_blue",
        "tool.memory": "green",
        "tool.mcp": "bright_cyan",
        #code bloclks
        "code": "white",

    }
)