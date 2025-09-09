"""
Integration tests for error handling in the dependency injection container.

Tests focus on error scenarios, exception handling, and error message quality.
"""

import pytest

from promptbin.core.container import ServiceContainer
from promptbin.core.exceptions import (
    ServiceResolutionError,
    CircularDependencyError,
    ServiceRegistrationError,
)


class TestErrorHandling:
    """Integration tests for container error handling."""

    def setup_method(self):
        """Set up fresh container for each test."""
        self.container = ServiceContainer()

    def test_missing_dependency_error_message_quality(self):
        """Test that missing dependency errors provide helpful information."""

        class ServiceA:
            pass

        class ServiceB:
            pass

        class MissingService:
            pass

        # Register some services but not the one we'll try to resolve
        self.container.register_singleton(ServiceA, lambda c: ServiceA())
        self.container.register_transient(ServiceB, lambda c: ServiceB())

        # Try to resolve unregistered service
        with pytest.raises(ServiceResolutionError) as exc_info:
            self.container.resolve(MissingService)

        error = exc_info.value
        error_message = str(error)

        # Error should contain helpful information
        assert "MissingService" in error_message
        assert "ServiceA" in error_message
        assert "ServiceB" in error_message
        assert "Available services" in error_message
        assert "Ensure the service is registered" in error_message

        # Error should have proper attributes
        assert error.service_type == MissingService
        assert ServiceA in error.available_services
        assert ServiceB in error.available_services
        assert MissingService not in error.available_services

    def test_circular_dependency_error_details(self):
        """Test circular dependency error provides complete chain information."""

        class ServiceA:
            def __init__(self, service_b):
                self.service_b = service_b

        class ServiceB:
            def __init__(self, service_c):
                self.service_c = service_c

        class ServiceC:
            def __init__(self, service_a):
                self.service_a = service_a

        # Create three-way circular dependency
        self.container.register_singleton(
            ServiceA, lambda c: ServiceA(c.resolve(ServiceB))
        )
        self.container.register_singleton(
            ServiceB, lambda c: ServiceB(c.resolve(ServiceC))
        )
        self.container.register_singleton(
            ServiceC, lambda c: ServiceC(c.resolve(ServiceA))
        )

        # Should detect circular dependency
        with pytest.raises(CircularDependencyError) as exc_info:
            self.container.resolve(ServiceA)

        error = exc_info.value
        error_message = str(error)

        # Should show complete dependency chain
        assert "ServiceA" in error_message
        assert "ServiceB" in error_message
        assert "ServiceC" in error_message
        assert "->" in error_message
        assert "Circular dependency detected" in error_message
        assert "Review your service dependencies" in error_message

        # Error should have proper chain
        assert len(error.dependency_chain) >= 2
        assert ServiceA in error.dependency_chain

    def test_factory_error_context_preservation(self):
        """Test that factory errors preserve original context."""

        class FailingService:
            def __init__(self):
                raise ValueError("Database connection failed")

        self.container.register_singleton(FailingService, lambda c: FailingService())

        # Should wrap original error with context
        with pytest.raises(ServiceRegistrationError) as exc_info:
            self.container.resolve(FailingService)

        error = exc_info.value
        error_message = str(error)

        # Should preserve original error information
        assert "FailingService" in error_message
        assert "Factory function failed" in error_message
        assert isinstance(error.original_error, ValueError)
        assert str(error.original_error) == "Database connection failed"

    def test_nested_dependency_error_propagation(self):
        """Test error propagation in nested dependency resolution."""

        class DatabaseService:
            def __init__(self):
                raise ConnectionError("Cannot connect to database")

        class RepositoryService:
            def __init__(self, db):
                self.db = db

        class BusinessService:
            def __init__(self, repo):
                self.repo = repo

        # Register services with nested dependencies
        self.container.register_singleton(DatabaseService, lambda c: DatabaseService())
        self.container.register_singleton(
            RepositoryService,
            lambda c: RepositoryService(c.resolve(DatabaseService)),
        )
        self.container.register_singleton(
            BusinessService,
            lambda c: BusinessService(c.resolve(RepositoryService)),
        )

        # Should fail when trying to resolve top-level service
        with pytest.raises(ServiceRegistrationError) as exc_info:
            self.container.resolve(BusinessService)

        # Should indicate which service failed (the database service)
        error = exc_info.value
        assert "DatabaseService" in str(error) or "RepositoryService" in str(error)

        # Original error should be preserved somewhere in the chain
        assert isinstance(error.original_error, ServiceRegistrationError) or isinstance(
            error.original_error, ConnectionError
        )

    def test_empty_container_error_message(self):
        """Test error message when resolving from empty container."""

        class SomeService:
            pass

        # Try to resolve from empty container
        with pytest.raises(ServiceResolutionError) as exc_info:
            self.container.resolve(SomeService)

        error = exc_info.value
        error_message = str(error)

        # Should indicate no services are available
        assert "SomeService" in error_message
        assert "[]" in error_message or "Available services: []" in error_message

    def test_multiple_error_scenarios_in_sequence(self):
        """Test container state after various error scenarios."""

        class WorkingService:
            def __init__(self):
                self.status = "working"

        class FailingService:
            def __init__(self):
                raise RuntimeError("Service failed")

        # Register both services
        self.container.register_singleton(WorkingService, lambda c: WorkingService())
        self.container.register_singleton(FailingService, lambda c: FailingService())

        # Working service should resolve successfully
        working = self.container.resolve(WorkingService)
        assert working.status == "working"

        # Failing service should raise error
        with pytest.raises(ServiceRegistrationError):
            self.container.resolve(FailingService)

        # Working service should still work after error
        working2 = self.container.resolve(WorkingService)
        assert working2 is working  # Same singleton instance

        # Container should report both services as registered
        assert self.container.is_registered(WorkingService)
        assert self.container.is_registered(FailingService)


class TestExceptionClasses:
    """Test the exception classes themselves."""

    def test_service_resolution_error(self):
        """Test ServiceResolutionError construction and attributes."""

        class ServiceA:
            pass

        class ServiceB:
            pass

        error = ServiceResolutionError(ServiceA, [ServiceB])

        assert error.service_type == ServiceA
        assert error.available_services == [ServiceB]
        assert "ServiceA" in str(error)
        assert "ServiceB" in str(error)

    def test_circular_dependency_error(self):
        """Test CircularDependencyError construction and attributes."""

        class ServiceA:
            pass

        class ServiceB:
            pass

        chain = [ServiceA, ServiceB]
        error = CircularDependencyError(chain)

        assert error.dependency_chain == chain
        assert "ServiceA" in str(error)
        assert "ServiceB" in str(error)
        assert "->" in str(error)

    def test_circular_dependency_error_empty_chain(self):
        """Test CircularDependencyError with empty chain."""

        error = CircularDependencyError([])

        assert error.dependency_chain == []
        assert "Circular dependency detected" in str(error)

    def test_service_registration_error(self):
        """Test ServiceRegistrationError construction and attributes."""

        class TestService:
            pass

        original_error = ValueError("Original error")
        error = ServiceRegistrationError(TestService, "Test reason", original_error)

        assert error.service_type == TestService
        assert error.reason == "Test reason"
        assert error.original_error == original_error
        assert "TestService" in str(error)
        assert "Test reason" in str(error)
        assert "Original error" in str(error)

    def test_service_registration_error_no_original(self):
        """Test ServiceRegistrationError without original error."""

        class TestService:
            pass

        error = ServiceRegistrationError(TestService, "Test reason")

        assert error.service_type == TestService
        assert error.reason == "Test reason"
        assert error.original_error is None
        assert "TestService" in str(error)
        assert "Test reason" in str(error)
