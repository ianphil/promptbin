"""
PromptBin - Easy-to-use MCP server for prompt management with web interface.

A reference implementation for MCP (Model Context Protocol) server integration with
comprehensive prompt management capabilities.
"""

__version__ = "0.3.4"
__author__ = "PromptBin Contributors"
__email__ = "noreply@promptbin.dev"

# Core exports
from .core.container import ServiceContainer, ServiceLifetime
from .core.exceptions import (
    ServiceResolutionError,
    CircularDependencyError,
    ServiceRegistrationError,
)

# Manager exports
from .managers.prompt_manager import PromptManager
from .managers.share_manager import ShareManager
from .managers.tunnel_manager import TunnelManager

__all__ = [
    "ServiceContainer",
    "ServiceLifetime",
    "ServiceResolutionError",
    "CircularDependencyError",
    "ServiceRegistrationError",
    "PromptManager",
    "ShareManager",
    "TunnelManager",
]
