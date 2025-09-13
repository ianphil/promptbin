"""
Centralized configuration management for PromptBin.

Provides a unified configuration system that consolidates all environment variables
with validation, type conversion, and sensible defaults.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from .exceptions import ServiceRegistrationError


@dataclass
class PromptBinConfig:
    """
    Centralized configuration for PromptBin application.

    Consolidates all environment variables with proper type conversion,
    validation, and sensible defaults for all configuration options.
    """

    # Flask/Web configuration
    flask_host: str = "127.0.0.1"
    flask_port: int = 5001
    secret_key: str = "dev-secret-key-change-in-production"

    # Core application configuration
    data_dir: str = "~/promptbin-data"
    log_level: str = "INFO"

    # Dev Tunnels configuration
    devtunnel_enabled: bool = True
    devtunnel_auto_start: bool = False
    devtunnel_rate_limit: int = 5
    devtunnel_rate_window: int = 30  # minutes
    devtunnel_log_level: str = "INFO"

    # MCP server configuration
    health_check_interval: int = 30  # seconds
    shutdown_timeout: int = 10  # seconds

    @classmethod
    def from_environment(cls) -> "PromptBinConfig":
        """
        Create configuration instance from environment variables.

        Reads all relevant environment variables with proper type conversion
        and falls back to sensible defaults.

        Returns:
            PromptBinConfig: Configuration instance with values from environment

        Raises:
            ServiceRegistrationError: If environment variable conversion fails
        """
        try:
            return cls(
                # Flask/Web configuration
                flask_host=os.environ.get("PROMPTBIN_HOST", "127.0.0.1"),
                flask_port=int(
                    os.environ.get(
                        "FLASK_RUN_PORT", os.environ.get("PROMPTBIN_PORT", "5001")
                    )
                ),
                secret_key=os.environ.get(
                    "SECRET_KEY", "dev-secret-key-change-in-production"
                ),
                # Core application configuration
                data_dir=os.environ.get("PROMPTBIN_DATA_DIR", "~/promptbin-data"),
                log_level=os.environ.get("PROMPTBIN_LOG_LEVEL", "INFO").upper(),
                # Dev Tunnels configuration
                devtunnel_enabled=os.environ.get("DEVTUNNEL_ENABLED", "true").lower()
                == "true",
                devtunnel_auto_start=os.environ.get(
                    "DEVTUNNEL_AUTO_START", "false"
                ).lower()
                == "true",
                devtunnel_rate_limit=int(os.environ.get("DEVTUNNEL_RATE_LIMIT", "5")),
                devtunnel_rate_window=int(
                    os.environ.get("DEVTUNNEL_RATE_WINDOW", "30")
                ),
                devtunnel_log_level=os.environ.get(
                    "DEVTUNNEL_LOG_LEVEL", "INFO"
                ).upper(),
                # MCP server configuration
                health_check_interval=int(
                    os.environ.get("PROMPTBIN_HEALTH_CHECK_INTERVAL", "30")
                ),
                shutdown_timeout=int(
                    os.environ.get("PROMPTBIN_SHUTDOWN_TIMEOUT", "10")
                ),
            )
        except (ValueError, TypeError) as e:
            raise ServiceRegistrationError(
                PromptBinConfig,
                f"Failed to parse configuration from environment: {e}",
                e,
            ) from e

    def validate(self) -> None:
        """
        Validate configuration values and raise errors for invalid states.

        Raises:
            ServiceRegistrationError: If any configuration values are invalid
        """
        errors = []

        # Validate port range
        if not (1024 <= self.flask_port <= 65535):
            errors.append(f"Flask port {self.flask_port} must be between 1024-65535")

        # Validate log levels
        valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.log_level not in valid_log_levels:
            errors.append(
                f"Log level '{self.log_level}' must be one of {valid_log_levels}"
            )
        if self.devtunnel_log_level not in valid_log_levels:
            errors.append(
                f"Devtunnel log level '{self.devtunnel_log_level}' must be one of "
                f"{valid_log_levels}"
            )

        # Validate data directory
        try:
            expanded_data_dir = Path(self.data_dir).expanduser()
            if not expanded_data_dir.parent.exists():
                errors.append(
                    f"Parent directory of data_dir '{expanded_data_dir.parent}' "
                    f"does not exist"
                )
        except (OSError, ValueError) as e:
            errors.append(f"Invalid data_dir path '{self.data_dir}': {e}")

        # Validate rate limiting parameters
        if self.devtunnel_rate_limit < 1:
            errors.append(
                f"Devtunnel rate limit {self.devtunnel_rate_limit} must be >= 1"
            )
        if self.devtunnel_rate_window < 1:
            errors.append(
                f"Devtunnel rate window {self.devtunnel_rate_window} must be "
                f">= 1 minute"
            )

        # Validate timeout parameters
        if self.health_check_interval < 5:
            errors.append(
                f"Health check interval {self.health_check_interval} must be "
                f">= 5 seconds"
            )
        if self.shutdown_timeout < 1:
            errors.append(
                f"Shutdown timeout {self.shutdown_timeout} must be >= 1 second"
            )

        if errors:
            raise ServiceRegistrationError(
                PromptBinConfig, f"Configuration validation failed: {'; '.join(errors)}"
            )

    def get_expanded_data_dir(self) -> Path:
        """
        Get the data directory path with user directory expansion.

        Returns:
            Path: Expanded data directory path
        """
        return Path(self.data_dir).expanduser()

    def to_dict(self) -> dict:
        """
        Convert configuration to dictionary for serialization.

        Returns:
            dict: Configuration as dictionary
        """
        return {
            "flask_host": self.flask_host,
            "flask_port": self.flask_port,
            "secret_key": (
                "***REDACTED***"
                if self.secret_key != "dev-secret-key-change-in-production"
                else self.secret_key
            ),
            "data_dir": self.data_dir,
            "log_level": self.log_level,
            "devtunnel_enabled": self.devtunnel_enabled,
            "devtunnel_auto_start": self.devtunnel_auto_start,
            "devtunnel_rate_limit": self.devtunnel_rate_limit,
            "devtunnel_rate_window": self.devtunnel_rate_window,
            "devtunnel_log_level": self.devtunnel_log_level,
            "health_check_interval": self.health_check_interval,
            "shutdown_timeout": self.shutdown_timeout,
        }

    def __post_init__(self):
        """Post-initialization validation."""
        # Allow creation of invalid configs for testing by setting _skip_validation
        if not getattr(self, "_skip_validation", False):
            self.validate()


def create_config() -> PromptBinConfig:
    """
    Factory function to create and validate configuration.

    Returns:
        PromptBinConfig: Validated configuration instance
    """
    config = PromptBinConfig.from_environment()
    config.validate()
    return config
