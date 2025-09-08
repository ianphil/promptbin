"""
Comprehensive unit tests for the ServiceContainer.

Tests cover service registration, resolution, lifecycle management,
error handling, and circular dependency detection.
"""

import pytest
from unittest.mock import Mock, MagicMock
import logging

from promptbin.core.container import ServiceContainer, ServiceLifetime
from promptbin.core.exceptions import (
    ServiceResolutionError,
    CircularDependencyError,
    ServiceRegistrationError,
)


class TestServiceContainer:
    """Test suite for ServiceContainer functionality."""

    def setup_method(self):
        """Set up fresh container for each test."""
        self.container = ServiceContainer()

    def test_register_and_resolve_singleton(self):
        """Test singleton service registration and resolution."""

        class TestService:
            def __init__(self, value="test"):
                self.value = value

        # Register singleton service
        self.container.register_singleton(
            TestService, lambda c: TestService("singleton")
        )

        # Resolve multiple times
        instance1 = self.container.resolve(TestService)
        instance2 = self.container.resolve(TestService)

        # Should return same instance (singleton behavior)
        assert instance1 is instance2
        assert instance1.value == "singleton"

        # Verify registration info
        services = self.container.get_registered_services()
        assert TestService in services
        assert services[TestService] == ServiceLifetime.SINGLETON

    def test_register_and_resolve_transient(self):
        """Test transient service registration and resolution."""

        class TestService:
            def __init__(self, value="test"):
                self.value = value

        # Register transient service
        self.container.register_transient(
            TestService, lambda c: TestService("transient")
        )

        # Resolve multiple times
        instance1 = self.container.resolve(TestService)
        instance2 = self.container.resolve(TestService)

        # Should return different instances (transient behavior)
        assert instance1 is not instance2
        assert instance1.value == "transient"
        assert instance2.value == "transient"

        # Verify registration info
        services = self.container.get_registered_services()
        assert TestService in services
        assert services[TestService] == ServiceLifetime.TRANSIENT

    def test_dependency_injection_in_factory(self):
        """Test that factory functions receive container for dependency injection."""

        class DependencyService:
            def __init__(self):
                self.name = "dependency"

        class MainService:
            def __init__(self, dependency):
                self.dependency = dependency

        # Register dependency first
        self.container.register_singleton(
            DependencyService, lambda c: DependencyService()
        )

        # Register main service that depends on dependency
        self.container.register_singleton(
            MainService, lambda c: MainService(c.resolve(DependencyService))
        )

        # Resolve main service
        main = self.container.resolve(MainService)

        assert isinstance(main.dependency, DependencyService)
        assert main.dependency.name == "dependency"

    def test_circular_dependency_detection(self):
        """Test circular dependency detection and error reporting."""

        class ServiceA:
            def __init__(self, service_b):
                self.service_b = service_b

        class ServiceB:
            def __init__(self, service_a):
                self.service_a = service_a

        # Register services with circular dependency
        self.container.register_singleton(
            ServiceA, lambda c: ServiceA(c.resolve(ServiceB))
        )
        self.container.register_singleton(
            ServiceB, lambda c: ServiceB(c.resolve(ServiceA))
        )

        # Should raise CircularDependencyError
        with pytest.raises(CircularDependencyError) as exc_info:
            self.container.resolve(ServiceA)

        error = exc_info.value
        assert "ServiceA" in str(error)
        assert "ServiceB" in str(error)
        assert "Circular dependency detected" in str(error)
        assert len(error.dependency_chain) >= 2

    def test_missing_service_resolution_error(self):
        """Test error handling for missing service resolution."""

        class RegisteredService:
            pass

        class MissingService:
            pass

        # Register only one service
        self.container.register_singleton(
            RegisteredService, lambda c: RegisteredService()
        )

        # Try to resolve unregistered service
        with pytest.raises(ServiceResolutionError) as exc_info:
            self.container.resolve(MissingService)

        error = exc_info.value
        assert error.service_type == MissingService
        assert RegisteredService in error.available_services
        assert "MissingService" in str(error)
        assert "RegisteredService" in str(error)

    def test_service_registration_error_invalid_factory(self):
        """Test error handling for invalid factory functions."""

        class TestService:
            pass

        # Try to register with non-callable factory
        with pytest.raises(ServiceRegistrationError) as exc_info:
            self.container.register_singleton(TestService, "not_callable")

        error = exc_info.value
        assert error.service_type == TestService
        assert "Factory must be callable" in str(error)

    def test_factory_exception_handling(self):
        """Test error handling when factory function throws exception."""

        class TestService:
            def __init__(self):
                raise ValueError("Construction failed")

        # Register service with failing factory
        self.container.register_singleton(TestService, lambda c: TestService())

        # Should wrap factory exception in ServiceRegistrationError
        with pytest.raises(ServiceRegistrationError) as exc_info:
            self.container.resolve(TestService)

        error = exc_info.value
        assert error.service_type == TestService
        assert "Factory function failed" in str(error)
        assert isinstance(error.original_error, ValueError)

    def test_is_registered(self):
        """Test service registration checking."""

        class RegisteredService:
            pass

        class UnregisteredService:
            pass

        # Initially nothing registered
        assert not self.container.is_registered(RegisteredService)
        assert not self.container.is_registered(UnregisteredService)

        # Register one service
        self.container.register_singleton(
            RegisteredService, lambda c: RegisteredService()
        )

        # Check registration status
        assert self.container.is_registered(RegisteredService)
        assert not self.container.is_registered(UnregisteredService)

    def test_clear_container(self):
        """Test clearing container state."""

        class TestService:
            pass

        # Register service and resolve to create singleton instance
        self.container.register_singleton(TestService, lambda c: TestService())
        instance1 = self.container.resolve(TestService)

        assert self.container.is_registered(TestService)

        # Clear container
        self.container.clear()

        # Should be empty now
        assert not self.container.is_registered(TestService)
        assert len(self.container.get_registered_services()) == 0

        # Re-registering should work and create new instance
        self.container.register_singleton(TestService, lambda c: TestService())
        instance2 = self.container.resolve(TestService)

        assert instance1 is not instance2

    def test_complex_dependency_graph(self):
        """Test resolution of complex dependency graphs."""

        class DatabaseService:
            def __init__(self):
                self.connected = True

        class LoggingService:
            def __init__(self):
                self.enabled = True

        class RepositoryService:
            def __init__(self, db, logger):
                self.db = db
                self.logger = logger

        class BusinessService:
            def __init__(self, repo, logger):
                self.repo = repo
                self.logger = logger

        # Register all services
        self.container.register_singleton(DatabaseService, lambda c: DatabaseService())
        self.container.register_singleton(LoggingService, lambda c: LoggingService())
        self.container.register_singleton(
            RepositoryService,
            lambda c: RepositoryService(
                c.resolve(DatabaseService), c.resolve(LoggingService)
            ),
        )
        self.container.register_transient(
            BusinessService,
            lambda c: BusinessService(
                c.resolve(RepositoryService), c.resolve(LoggingService)
            ),
        )

        # Resolve business service
        business1 = self.container.resolve(BusinessService)
        business2 = self.container.resolve(BusinessService)

        # Verify dependency injection worked
        assert business1.repo.db.connected
        assert business1.repo.logger.enabled
        assert business1.logger.enabled

        # Business service should be transient (different instances)
        assert business1 is not business2

        # But shared dependencies should be singletons
        assert business1.repo is business2.repo
        assert business1.logger is business2.logger
        assert business1.repo.db is business2.repo.db

    def test_logging_integration(self, caplog):
        """Test that container logs service lifecycle events."""

        class TestService:
            pass

        with caplog.at_level(logging.DEBUG):
            # Register and resolve service
            self.container.register_singleton(TestService, lambda c: TestService())
            self.container.resolve(TestService)

            # Check for expected log messages
            assert "Registered singleton service: TestService" in caplog.text
            assert "Creating singleton service: TestService" in caplog.text
            assert "Successfully resolved service: TestService" in caplog.text

            # Second resolution should use cached instance
            caplog.clear()
            self.container.resolve(TestService)
            assert "Returning cached singleton: TestService" in caplog.text


class TestServiceRegistration:
    """Test suite for ServiceRegistration internal class."""

    def test_service_registration_creation(self):
        """Test ServiceRegistration object creation."""
        from promptbin.core.container import ServiceRegistration

        class TestService:
            pass

        factory = lambda c: TestService()
        registration = ServiceRegistration(
            TestService, factory, ServiceLifetime.SINGLETON
        )

        assert registration.service_type == TestService
        assert registration.factory == factory
        assert registration.lifetime == ServiceLifetime.SINGLETON

    def test_service_registration_create_instance(self):
        """Test ServiceRegistration instance creation."""
        from promptbin.core.container import ServiceRegistration

        class TestService:
            def __init__(self, value):
                self.value = value

        factory = lambda c: TestService("test_value")
        registration = ServiceRegistration(
            TestService, factory, ServiceLifetime.TRANSIENT
        )

        container = Mock()
        instance = registration.create_instance(container)

        assert isinstance(instance, TestService)
        assert instance.value == "test_value"

    def test_service_registration_factory_error(self):
        """Test ServiceRegistration error handling for factory failures."""
        from promptbin.core.container import ServiceRegistration

        class TestService:
            pass

        def failing_factory(container):
            raise ValueError("Factory failed")

        registration = ServiceRegistration(
            TestService, failing_factory, ServiceLifetime.SINGLETON
        )
        container = Mock()

        with pytest.raises(ServiceRegistrationError) as exc_info:
            registration.create_instance(container)

        error = exc_info.value
        assert error.service_type == TestService
        assert "Factory function failed" in str(error)
        assert isinstance(error.original_error, ValueError)
