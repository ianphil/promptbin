"""
Integration tests for PromptBin configuration with ServiceContainer.

Tests the integration between the configuration system and dependency injection,
including service registration and resolution scenarios.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from promptbin.core.config import PromptBinConfig, create_config
from promptbin.core.container import ServiceContainer
from promptbin.core.exceptions import ServiceRegistrationError, ServiceResolutionError


class TestConfigurationServiceIntegration:
    """Test configuration integration with ServiceContainer."""

    def setup_method(self):
        """Set up a fresh container for each test."""
        self.container = ServiceContainer()

    def test_register_config_success(self):
        """Test successful configuration registration."""
        with patch.dict(os.environ, {}, clear=True):
            self.container.register_config()

            assert self.container.is_registered(PromptBinConfig)

            # Should be registered as singleton
            registered_services = self.container.get_registered_services()
            from promptbin.core.container import ServiceLifetime

            assert registered_services[PromptBinConfig] == ServiceLifetime.SINGLETON

    def test_resolve_config_success(self):
        """Test successful configuration resolution."""
        with patch.dict(os.environ, {}, clear=True):
            self.container.register_config()

            config = self.container.resolve(PromptBinConfig)

            assert isinstance(config, PromptBinConfig)
            assert config.flask_host == "127.0.0.1"
            assert config.flask_port == 5001

    def test_resolve_config_singleton_behavior(self):
        """Test that resolved configuration instances are singletons."""
        with patch.dict(os.environ, {}, clear=True):
            self.container.register_config()

            config1 = self.container.resolve(PromptBinConfig)
            config2 = self.container.resolve(PromptBinConfig)

            # Should be the exact same instance
            assert config1 is config2

    def test_resolve_config_with_environment_variables(self):
        """Test configuration resolution with environment variables."""
        env_vars = {
            "PROMPTBIN_HOST": "0.0.0.0",
            "PROMPTBIN_PORT": "8080",
            "PROMPTBIN_LOG_LEVEL": "DEBUG",
        }

        with patch.dict(os.environ, env_vars):
            self.container.register_config()
            config = self.container.resolve(PromptBinConfig)

            assert config.flask_host == "0.0.0.0"
            assert config.flask_port == 8080
            assert config.log_level == "DEBUG"

    def test_config_validation_during_resolution(self):
        """Test that invalid configuration fails during resolution."""
        with patch.dict(os.environ, {"PROMPTBIN_PORT": "80"}):  # Invalid port
            self.container.register_config()
            with pytest.raises(
                ServiceRegistrationError, match="Configuration validation failed"
            ):
                self.container.resolve(PromptBinConfig)

    def test_resolve_config_not_registered(self):
        """Test that resolving unregistered config raises appropriate error."""
        with pytest.raises(ServiceResolutionError):
            self.container.resolve(PromptBinConfig)

    def test_multiple_containers_independent_configs(self):
        """Test that different containers have independent configuration instances."""
        env_vars1 = {"PROMPTBIN_PORT": "3000"}
        env_vars2 = {"PROMPTBIN_PORT": "4000"}

        container1 = ServiceContainer()
        container2 = ServiceContainer()

        with patch.dict(os.environ, env_vars1):
            container1.register_config()
            config1 = container1.resolve(PromptBinConfig)

        with patch.dict(os.environ, env_vars2):
            container2.register_config()
            config2 = container2.resolve(PromptBinConfig)

        assert config1.flask_port == 3000
        assert config2.flask_port == 4000
        assert config1 is not config2


class TestDependentServiceIntegration:
    """Test services that depend on configuration."""

    def setup_method(self):
        """Set up a fresh container for each test."""
        self.container = ServiceContainer()

    def test_service_with_config_dependency(self):
        """Test a service that depends on configuration."""

        class TestService:
            def __init__(self, config: PromptBinConfig):
                self.config = config
                self.port = config.flask_port

        # Register configuration and dependent service
        with patch.dict(os.environ, {"PROMPTBIN_PORT": "9000"}):
            self.container.register_config()
            self.container.register_singleton(
                TestService,
                lambda container: TestService(container.resolve(PromptBinConfig)),
            )

            service = self.container.resolve(TestService)

            assert isinstance(service.config, PromptBinConfig)
            assert service.port == 9000

    def test_multiple_services_shared_config(self):
        """Test multiple services sharing the same configuration instance."""

        class ServiceA:
            def __init__(self, config: PromptBinConfig):
                self.config = config

        class ServiceB:
            def __init__(self, config: PromptBinConfig):
                self.config = config

        with patch.dict(os.environ, {}, clear=True):
            self.container.register_config()

            self.container.register_singleton(
                ServiceA, lambda container: ServiceA(container.resolve(PromptBinConfig))
            )

            self.container.register_singleton(
                ServiceB, lambda container: ServiceB(container.resolve(PromptBinConfig))
            )

            service_a = self.container.resolve(ServiceA)
            service_b = self.container.resolve(ServiceB)

            # Both services should share the same config instance
            assert service_a.config is service_b.config

    def test_transient_service_shared_config(self):
        """Test transient services still share the same singleton config."""

        class TransientService:
            def __init__(self, config: PromptBinConfig):
                self.config = config

        with patch.dict(os.environ, {}, clear=True):
            self.container.register_config()

            self.container.register_transient(
                TransientService,
                lambda container: TransientService(container.resolve(PromptBinConfig)),
            )

            service1 = self.container.resolve(TransientService)
            service2 = self.container.resolve(TransientService)

            # Services are different instances (transient)
            assert service1 is not service2

            # But they share the same config instance (singleton)
            assert service1.config is service2.config


class TestConfigurationErrorHandling:
    """Test error handling scenarios in configuration integration."""

    def setup_method(self):
        """Set up a fresh container for each test."""
        self.container = ServiceContainer()

    def test_config_creation_failure_during_resolution(self):
        """Test handling of configuration creation failure during resolution."""
        with patch("promptbin.core.config.create_config") as mock_create:
            mock_create.side_effect = ServiceRegistrationError(
                PromptBinConfig, "Test error"
            )

            self.container.register_config()
            with pytest.raises(ServiceRegistrationError, match="Test error"):
                self.container.resolve(PromptBinConfig)

    def test_config_validation_failure_cascades_to_dependents(self):
        """Test that config validation failures prevent dependent service creation."""

        class DependentService:
            def __init__(self, config: PromptBinConfig):
                self.config = config

        # Register services with invalid configuration
        with patch.dict(os.environ, {"PROMPTBIN_PORT": "invalid"}):
            self.container.register_config()

            self.container.register_singleton(
                DependentService,
                lambda container: DependentService(container.resolve(PromptBinConfig)),
            )

            # Resolution should fail due to invalid config
            with pytest.raises(
                ServiceRegistrationError, match="Failed to parse configuration"
            ):
                self.container.resolve(DependentService)

    def test_config_resolution_failure_in_dependent_service(self):
        """Test handling when config resolution fails in dependent service factory."""

        class FailingService:
            def __init__(self, config: PromptBinConfig):
                # Simulate failure during service creation
                raise ValueError("Service initialization failed")

        with patch.dict(os.environ, {}, clear=True):
            self.container.register_config()

            self.container.register_singleton(
                FailingService,
                lambda container: FailingService(container.resolve(PromptBinConfig)),
            )

            with pytest.raises(
                ServiceRegistrationError, match="Factory function failed"
            ):
                self.container.resolve(FailingService)


class TestRealWorldIntegrationScenarios:
    """Test realistic integration scenarios."""

    def setup_method(self):
        """Set up a fresh container for each test."""
        self.container = ServiceContainer()

    def test_tunnel_manager_integration_pattern(self):
        """Test the pattern used by TunnelManager integration."""

        # Mock TunnelManager-like service
        class MockTunnelManager:
            def __init__(self, flask_port: int, config: PromptBinConfig = None):
                self.flask_port = flask_port
                self.config = config
                if config:
                    self.enabled = config.devtunnel_enabled
                    self.rate_limit = config.devtunnel_rate_limit
                else:
                    # Backward compatibility fallback
                    self.enabled = True
                    self.rate_limit = 5

        env_vars = {"DEVTUNNEL_ENABLED": "false", "DEVTUNNEL_RATE_LIMIT": "10"}

        with patch.dict(os.environ, env_vars):
            self.container.register_config()

            self.container.register_singleton(
                MockTunnelManager,
                lambda container: MockTunnelManager(
                    flask_port=5001, config=container.resolve(PromptBinConfig)
                ),
            )

            tunnel_manager = self.container.resolve(MockTunnelManager)

            assert tunnel_manager.flask_port == 5001
            assert tunnel_manager.enabled is False
            assert tunnel_manager.rate_limit == 10
            assert isinstance(tunnel_manager.config, PromptBinConfig)

    def test_flask_app_initialization_pattern(self):
        """Test the pattern used for Flask app initialization."""

        # Mock Flask app initialization
        class MockFlaskApp:
            def __init__(self, config: PromptBinConfig):
                self.config_dict = {
                    "SECRET_KEY": config.secret_key,
                    "HOST": config.flask_host,
                    "PORT": config.flask_port,
                    "DATA_DIR": str(config.get_expanded_data_dir()),
                }

        env_vars = {
            "SECRET_KEY": "test-secret-key",
            "PROMPTBIN_HOST": "localhost",
            "PROMPTBIN_PORT": "3000",
            "PROMPTBIN_DATA_DIR": "/tmp/test-data",
        }

        with patch.dict(os.environ, env_vars):
            self.container.register_config()

            self.container.register_singleton(
                MockFlaskApp,
                lambda container: MockFlaskApp(container.resolve(PromptBinConfig)),
            )

            app = self.container.resolve(MockFlaskApp)

            assert app.config_dict["SECRET_KEY"] == "test-secret-key"
            assert app.config_dict["HOST"] == "localhost"
            assert app.config_dict["PORT"] == 3000
            assert app.config_dict["DATA_DIR"] == "/tmp/test-data"

    def test_mcp_server_initialization_pattern(self):
        """Test the pattern used for MCP server initialization."""

        # Mock MCP server
        class MockMCPServer:
            def __init__(self, config: PromptBinConfig):
                self.host = config.flask_host
                self.port = config.flask_port
                self.data_dir = str(config.get_expanded_data_dir())
                self.log_level = config.log_level
                self.health_check_interval = config.health_check_interval

        env_vars = {
            "PROMPTBIN_HOST": "0.0.0.0",
            "PROMPTBIN_PORT": "8080",
            "PROMPTBIN_LOG_LEVEL": "DEBUG",
            "PROMPTBIN_HEALTH_CHECK_INTERVAL": "60",
        }

        with patch.dict(os.environ, env_vars):
            self.container.register_config()

            self.container.register_singleton(
                MockMCPServer,
                lambda container: MockMCPServer(container.resolve(PromptBinConfig)),
            )

            server = self.container.resolve(MockMCPServer)

            assert server.host == "0.0.0.0"
            assert server.port == 8080
            assert server.log_level == "DEBUG"
            assert server.health_check_interval == 60
