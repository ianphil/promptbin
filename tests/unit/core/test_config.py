"""
Unit tests for PromptBin configuration management.

Tests configuration loading, validation, environment variable handling,
and integration with the service container.
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from tempfile import TemporaryDirectory

from promptbin.core.config import PromptBinConfig, create_config
from promptbin.core.exceptions import ServiceRegistrationError


class TestPromptBinConfig:
    """Test cases for PromptBinConfig class."""

    def test_default_configuration(self):
        """Test that default configuration has expected values."""
        config = PromptBinConfig()

        assert config.flask_host == "127.0.0.1"
        assert config.flask_port == 5001
        assert config.secret_key == "dev-secret-key-change-in-production"
        assert config.data_dir == "~/promptbin-data"
        assert config.log_level == "INFO"
        assert config.devtunnel_enabled is True
        assert config.devtunnel_auto_start is False
        assert config.devtunnel_rate_limit == 5
        assert config.devtunnel_rate_window == 30
        assert config.devtunnel_log_level == "INFO"
        assert config.health_check_interval == 30
        assert config.shutdown_timeout == 10

    def test_from_environment_default_values(self):
        """Test loading configuration from environment with default values."""
        with patch.dict(os.environ, {}, clear=True):
            config = PromptBinConfig.from_environment()

            assert config.flask_host == "127.0.0.1"
            assert config.flask_port == 5001
            assert config.log_level == "INFO"

    def test_from_environment_with_overrides(self):
        """Test loading configuration with environment variable overrides."""
        env_vars = {
            "PROMPTBIN_HOST": "0.0.0.0",
            "PROMPTBIN_PORT": "8080",
            "SECRET_KEY": "test-secret",
            "PROMPTBIN_DATA_DIR": "/tmp/test-data",
            "PROMPTBIN_LOG_LEVEL": "DEBUG",
            "DEVTUNNEL_ENABLED": "false",
            "DEVTUNNEL_AUTO_START": "true",
            "DEVTUNNEL_RATE_LIMIT": "10",
            "DEVTUNNEL_RATE_WINDOW": "60",
            "DEVTUNNEL_LOG_LEVEL": "WARNING",
        }

        with patch.dict(os.environ, env_vars):
            config = PromptBinConfig.from_environment()

            assert config.flask_host == "0.0.0.0"
            assert config.flask_port == 8080
            assert config.secret_key == "test-secret"
            assert config.data_dir == "/tmp/test-data"
            assert config.log_level == "DEBUG"
            assert config.devtunnel_enabled is False
            assert config.devtunnel_auto_start is True
            assert config.devtunnel_rate_limit == 10
            assert config.devtunnel_rate_window == 60
            assert config.devtunnel_log_level == "WARNING"

    def test_flask_run_port_precedence(self):
        """Test that FLASK_RUN_PORT takes precedence over PROMPTBIN_PORT."""
        env_vars = {
            "FLASK_RUN_PORT": "3000",
            "PROMPTBIN_PORT": "4000",
        }

        with patch.dict(os.environ, env_vars):
            config = PromptBinConfig.from_environment()
            assert config.flask_port == 3000

    def test_promptbin_port_fallback(self):
        """Test that PROMPTBIN_PORT is used when FLASK_RUN_PORT is not set."""
        env_vars = {"PROMPTBIN_PORT": "4000"}

        with patch.dict(os.environ, env_vars):
            config = PromptBinConfig.from_environment()
            assert config.flask_port == 4000

    def test_from_environment_invalid_port(self):
        """Test that invalid port values raise ServiceRegistrationError."""
        with patch.dict(os.environ, {"PROMPTBIN_PORT": "not-a-number"}):
            with pytest.raises(
                ServiceRegistrationError, match="Failed to parse configuration"
            ):
                PromptBinConfig.from_environment()

    def test_from_environment_invalid_boolean(self):
        """Test that invalid boolean values are handled gracefully."""
        with patch.dict(os.environ, {"DEVTUNNEL_ENABLED": "invalid"}):
            config = PromptBinConfig.from_environment()
            # Should default to False for non-"true" values
            assert config.devtunnel_enabled is False

    def test_validation_valid_config(self):
        """Test that valid configuration passes validation."""
        config = PromptBinConfig()
        # Should not raise any exception
        config.validate()

    def test_validation_invalid_port_range(self):
        """Test validation fails for ports outside valid range."""
        # Test port below 1024
        with pytest.raises(
            ServiceRegistrationError, match="Flask port 80 must be between 1024-65535"
        ):
            PromptBinConfig(flask_port=80)

        # Test port above 65535
        with pytest.raises(
            ServiceRegistrationError,
            match="Flask port 70000 must be between 1024-65535",
        ):
            PromptBinConfig(flask_port=70000)

    def test_validation_invalid_log_level(self):
        """Test validation fails for invalid log levels."""
        with pytest.raises(
            ServiceRegistrationError, match="Log level 'INVALID' must be one of"
        ):
            PromptBinConfig(log_level="INVALID")

    def test_validation_invalid_devtunnel_log_level(self):
        """Test validation fails for invalid devtunnel log levels."""
        with pytest.raises(
            ServiceRegistrationError,
            match="Devtunnel log level 'INVALID' must be one of",
        ):
            PromptBinConfig(devtunnel_log_level="INVALID")

    def test_validation_invalid_rate_limit(self):
        """Test validation fails for invalid rate limit values."""
        with pytest.raises(
            ServiceRegistrationError, match="Devtunnel rate limit 0 must be >= 1"
        ):
            PromptBinConfig(devtunnel_rate_limit=0)

    def test_validation_invalid_rate_window(self):
        """Test validation fails for invalid rate window values."""
        with pytest.raises(
            ServiceRegistrationError,
            match="Devtunnel rate window 0 must be >= 1 minute",
        ):
            PromptBinConfig(devtunnel_rate_window=0)

    def test_validation_invalid_timeouts(self):
        """Test validation fails for invalid timeout values."""
        with pytest.raises(
            ServiceRegistrationError,
            match="Health check interval 1 must be >= 5 seconds",
        ):
            PromptBinConfig(health_check_interval=1)

        with pytest.raises(
            ServiceRegistrationError, match="Shutdown timeout 0 must be >= 1 second"
        ):
            PromptBinConfig(shutdown_timeout=0)

    def test_validation_nonexistent_parent_directory(self):
        """Test validation fails when data directory parent doesn't exist."""
        with TemporaryDirectory() as temp_dir:
            nonexistent_path = f"{temp_dir}/nonexistent/data"
            with pytest.raises(
                ServiceRegistrationError, match="Parent directory of data_dir"
            ):
                PromptBinConfig(data_dir=nonexistent_path)

    def test_get_expanded_data_dir(self):
        """Test data directory expansion."""
        config = PromptBinConfig(data_dir="~/test-data")
        expanded = config.get_expanded_data_dir()

        assert isinstance(expanded, Path)
        assert str(expanded).startswith(str(Path.home()))
        assert str(expanded).endswith("test-data")

    def test_to_dict_redacts_secret_key(self):
        """Test that to_dict() redacts production secret keys."""
        config = PromptBinConfig(secret_key="production-secret")
        config_dict = config.to_dict()

        assert config_dict["secret_key"] == "***REDACTED***"

    def test_to_dict_preserves_dev_secret_key(self):
        """Test that to_dict() preserves development secret key."""
        config = PromptBinConfig()  # Uses default dev key
        config_dict = config.to_dict()

        assert config_dict["secret_key"] == "dev-secret-key-change-in-production"

    def test_to_dict_contains_all_fields(self):
        """Test that to_dict() contains all expected configuration fields."""
        config = PromptBinConfig()
        config_dict = config.to_dict()

        expected_fields = {
            "flask_host",
            "flask_port",
            "secret_key",
            "data_dir",
            "log_level",
            "devtunnel_enabled",
            "devtunnel_auto_start",
            "devtunnel_rate_limit",
            "devtunnel_rate_window",
            "devtunnel_log_level",
            "health_check_interval",
            "shutdown_timeout",
        }

        assert set(config_dict.keys()) == expected_fields

    def test_post_init_validation(self):
        """Test that __post_init__ calls validation."""
        with pytest.raises(
            ServiceRegistrationError, match="Flask port 80 must be between 1024-65535"
        ):
            PromptBinConfig(flask_port=80)  # Invalid port should fail immediately


class TestCreateConfig:
    """Test cases for create_config factory function."""

    def test_create_config_success(self):
        """Test successful configuration creation."""
        with patch.dict(os.environ, {}, clear=True):
            config = create_config()

            assert isinstance(config, PromptBinConfig)
            assert config.flask_host == "127.0.0.1"
            assert config.flask_port == 5001

    def test_create_config_with_environment_variables(self):
        """Test configuration creation with environment variables."""
        env_vars = {
            "PROMPTBIN_HOST": "localhost",
            "PROMPTBIN_PORT": "3000",
        }

        with patch.dict(os.environ, env_vars):
            config = create_config()

            assert config.flask_host == "localhost"
            assert config.flask_port == 3000

    def test_create_config_validation_failure(self):
        """Test that create_config raises error for invalid configuration."""
        with patch.dict(os.environ, {"PROMPTBIN_PORT": "80"}):  # Invalid port
            with pytest.raises(ServiceRegistrationError):
                create_config()


class TestEnvironmentVariableHandling:
    """Test specific environment variable handling scenarios."""

    def test_boolean_parsing_variations(self):
        """Test various boolean value formats."""
        test_cases = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("false", False),
            ("False", False),
            ("FALSE", False),
            ("1", False),  # Only "true" should be True
            ("0", False),
            ("yes", False),
            ("", False),
        ]

        for env_value, expected in test_cases:
            with patch.dict(os.environ, {"DEVTUNNEL_ENABLED": env_value}):
                config = PromptBinConfig.from_environment()
                assert config.devtunnel_enabled is expected, f"Failed for '{env_value}'"

    def test_integer_parsing_edge_cases(self):
        """Test integer parsing for various edge cases."""
        # Valid integers
        with patch.dict(os.environ, {"DEVTUNNEL_RATE_LIMIT": "1"}):
            config = PromptBinConfig.from_environment()
            assert config.devtunnel_rate_limit == 1

        with patch.dict(os.environ, {"DEVTUNNEL_RATE_LIMIT": "9999"}):
            config = PromptBinConfig.from_environment()
            assert config.devtunnel_rate_limit == 9999

    def test_log_level_case_normalization(self):
        """Test that log levels are normalized to uppercase."""
        test_cases = ["debug", "DEBUG", "info", "INFO", "warning", "error"]

        for level in test_cases:
            with patch.dict(os.environ, {"PROMPTBIN_LOG_LEVEL": level}):
                config = PromptBinConfig.from_environment()
                assert config.log_level == level.upper()


class TestBackwardCompatibility:
    """Test backward compatibility scenarios."""

    def test_mixed_environment_variables(self):
        """Test handling of both old and new environment variable formats."""
        env_vars = {
            "FLASK_RUN_PORT": "3000",  # Old Flask style
            "PROMPTBIN_HOST": "0.0.0.0",  # New PromptBin style
            "SECRET_KEY": "test-key",  # Flask style
            "DEVTUNNEL_ENABLED": "false",  # DevTunnel style
        }

        with patch.dict(os.environ, env_vars):
            config = PromptBinConfig.from_environment()

            assert config.flask_port == 3000
            assert config.flask_host == "0.0.0.0"
            assert config.secret_key == "test-key"
            assert config.devtunnel_enabled is False

    def test_missing_optional_environment_variables(self):
        """Test handling when optional environment variables are missing."""
        # Test with minimal environment
        minimal_env = {"PROMPTBIN_HOST": "127.0.0.1", "PROMPTBIN_PORT": "5001"}

        with patch.dict(os.environ, minimal_env, clear=True):
            config = PromptBinConfig.from_environment()

            # Should use defaults for missing variables
            assert config.devtunnel_enabled is True
            assert config.devtunnel_rate_limit == 5
            assert config.log_level == "INFO"
