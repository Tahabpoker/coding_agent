from rich.console import Console
from rich.theme import Theme

_PALETTE = {
    "cyan": "cyan",
    "cyan_dim": "dim cyan",
    "cyan_bright": "bright_cyan",
    "blue_bright": "bright_blue",
    "magenta_bright": "bright_magenta",
    "yellow_bright": "bright_yellow",
    "red_bright": "bright_red",
    "green": "green",
    "grey_50": "grey50",
    "grey_37": "grey37",
    "white": "white",
}

AGENT_THEME = Theme(
    {
        "info": _PALETTE["cyan_dim"],
        "warning": "yellow",
        "error": f"{_PALETTE['red_bright']} bold",
        "success": _PALETTE["green"],
        "debug": _PALETTE["grey_50"],
        "dim": "dim",
        "muted": _PALETTE["grey_50"],
        "border": _PALETTE["grey_37"],
        "highlight": f"bold {_PALETTE['cyan']}",
        # Roles
        "user": f"{_PALETTE['blue_bright']} bold",
        "assistant": "bright_white",
        # Tools
        "tool": f"{_PALETTE['magenta_bright']} bold",
        "tool.read": _PALETTE["cyan"],
        "tool.write": _PALETTE["yellow_bright"],
        "tool.shell": "magenta",
        "tool.network": _PALETTE["blue_bright"],
        "tool.memory": _PALETTE["green"],
        "tool.mcp": _PALETTE["cyan_bright"],
        # Code blocks
        "code": _PALETTE["white"],
    }
)

def create_console() -> Console:
    """Create a consistent console configured for the agent theme."""
    return Console(theme=AGENT_THEME, highlight=False, soft_wrap=True)
