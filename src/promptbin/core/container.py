"""
Lightweight dependency injection container for PromptBin.

Provides service registration, resolution, and lifecycle management
with support for singleton and transient service lifecycles.
"""

import logging
from typing import Type, Callable, Dict, Set, Any, TypeVar
from enum import Enum

from .exceptions import (
    ServiceResolutionError,
    CircularDependencyError,
    ServiceRegistrationError,
)

# Type variable for service types
T = TypeVar("T")


class ServiceLifetime(Enum):
    """Service lifetime options for registration."""

    SINGLETON = "singleton"
    TRANSIENT = "transient"


class ServiceRegistration:
    """Internal representation of a service registration."""

    def __init__(
        self,
        service_type: Type,
        factory: Callable[["ServiceContainer"], Any],
        lifetime: ServiceLifetime,
    ):
        self.service_type = service_type
        self.factory = factory
        self.lifetime = lifetime

    def create_instance(self, container: "ServiceContainer") -> Any:
        """Create a new instance using the factory function."""
        try:
            return self.factory(container)
        except (ServiceResolutionError, CircularDependencyError):
            # Re-raise DI-related errors without wrapping
            raise
        except Exception as e:
            raise ServiceRegistrationError(
                self.service_type,
                "Factory function failed during service creation",
                e,
            )


class ServiceContainer:
    """
    Lightweight dependency injection container.

    Manages service registration, resolution, and lifecycle with support for:
    - Singleton and transient service lifecycles
    - Interface-based service registration
    - Circular dependency detection
    - Clear error messages for debugging
    """

    def __init__(self):
        """Initialize a new service container."""
        self._services: Dict[Type, ServiceRegistration] = {}
        self._singleton_instances: Dict[Type, Any] = {}
        self._resolving: Set[Type] = set()
        self._logger = logging.getLogger(f"{__name__}.ServiceContainer")

    def register_singleton(
        self, service_type: Type[T], factory: Callable[["ServiceContainer"], T]
    ) -> None:
        """
        Register a service with singleton lifetime.

        Args:
            service_type: The service interface/class to register
            factory: Function that creates the service instance, receives container

        Raises:
            ServiceRegistrationError: If registration fails
        """
        self._register_service(service_type, factory, ServiceLifetime.SINGLETON)

    def register_transient(
        self, service_type: Type[T], factory: Callable[["ServiceContainer"], T]
    ) -> None:
        """
        Register a service with transient lifetime.

        Args:
            service_type: The service interface/class to register
            factory: Function that creates the service instance, receives container

        Raises:
            ServiceRegistrationError: If registration fails
        """
        self._register_service(service_type, factory, ServiceLifetime.TRANSIENT)

    def _register_service(
        self, service_type: Type, factory: Callable, lifetime: ServiceLifetime
    ) -> None:
        """Internal method to register a service with specified lifetime."""
        try:
            if not callable(factory):
                raise ServiceRegistrationError(service_type, "Factory must be callable")

            registration = ServiceRegistration(service_type, factory, lifetime)
            self._services[service_type] = registration

            self._logger.debug(
                f"Registered {lifetime.value} service: {service_type.__name__}"
            )

        except Exception as e:
            if isinstance(e, ServiceRegistrationError):
                raise
            raise ServiceRegistrationError(service_type, "Registration failed", e)

    def resolve(self, service_type: Type[T]) -> T:
        """
        Resolve a service from the container.

        Args:
            service_type: The service interface/class to resolve

        Returns:
            Instance of the requested service

        Raises:
            ServiceResolutionError: If service cannot be resolved
            CircularDependencyError: If circular dependency detected
        """
        # Check for circular dependency
        if service_type in self._resolving:
            dependency_chain = list(self._resolving) + [service_type]
            raise CircularDependencyError(dependency_chain)

        # Check if service is registered
        if service_type not in self._services:
            available_services = list(self._services.keys())
            raise ServiceResolutionError(service_type, available_services)

        registration = self._services[service_type]

        # For singletons, return cached instance if available
        if registration.lifetime == ServiceLifetime.SINGLETON:
            if service_type in self._singleton_instances:
                self._logger.debug(
                    f"Returning cached singleton: {service_type.__name__}"
                )
                return self._singleton_instances[service_type]

        # Add to resolving set to detect circular dependencies
        self._resolving.add(service_type)

        try:
            # Create new instance
            self._logger.debug(
                f"Creating {registration.lifetime.value} service: "
                f"{service_type.__name__}"
            )
            instance = registration.create_instance(self)

            # Cache singleton instances
            if registration.lifetime == ServiceLifetime.SINGLETON:
                self._singleton_instances[service_type] = instance

            self._logger.debug(
                f"Successfully resolved service: {service_type.__name__}"
            )
            return instance

        finally:
            # Always remove from resolving set
            self._resolving.discard(service_type)

    def is_registered(self, service_type: Type) -> bool:
        """
        Check if a service type is registered.

        Args:
            service_type: The service interface/class to check

        Returns:
            True if the service is registered, False otherwise
        """
        return service_type in self._services

    def clear(self) -> None:
        """
        Clear all service registrations and cached instances.

        Primarily intended for testing scenarios where a fresh container state
        is needed.
        """
        self._services.clear()
        self._singleton_instances.clear()
        self._resolving.clear()
        self._logger.debug("Container cleared - all services and instances removed")

    def get_registered_services(self) -> Dict[Type, ServiceLifetime]:
        """
        Get information about all registered services.

        Returns:
            Dictionary mapping service types to their lifetimes
        """
        return {
            service_type: registration.lifetime
            for service_type, registration in self._services.items()
        }
