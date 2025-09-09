"""
Custom exceptions for the dependency injection container.

These exceptions provide clear, actionable error messages for common
container configuration and resolution issues.
"""

from typing import List, Type


class ServiceResolutionError(Exception):
    """Raised when a required service cannot be resolved from the container."""

    def __init__(self, service_type: Type, available_services: List[Type]):
        self.service_type = service_type
        self.available_services = available_services
        super().__init__(self._create_message())

    def _create_message(self) -> str:
        available_names = [s.__name__ for s in self.available_services]
        return (
            f"Cannot resolve service '{self.service_type.__name__}'. "
            f"Available services: {available_names}. "
            f"Ensure the service is registered before attempting to resolve it."
        )


class CircularDependencyError(Exception):
    """Raised when circular dependencies are detected during service resolution."""

    def __init__(self, dependency_chain: List[Type]):
        self.dependency_chain = dependency_chain
        super().__init__(self._create_message())

    def _create_message(self) -> str:
        if not self.dependency_chain:
            return "Circular dependency detected"

        chain_names = [service.__name__ for service in self.dependency_chain]
        chain_str = " -> ".join(chain_names)
        first_service = self.dependency_chain[0].__name__

        return (
            f"Circular dependency detected: {chain_str} -> {first_service}. "
            f"Review your service dependencies to break the circular reference."
        )


class ServiceRegistrationError(Exception):
    """Raised when service registration fails."""

    def __init__(
        self, service_type: Type, reason: str, original_error: Exception = None
    ):
        self.service_type = service_type
        self.reason = reason
        self.original_error = original_error
        super().__init__(self._create_message())

    def _create_message(self) -> str:
        message = (
            f"Failed to register service '{self.service_type.__name__}': {self.reason}"
        )
        if self.original_error:
            message += f" (Original error: {self.original_error})"
        return message
