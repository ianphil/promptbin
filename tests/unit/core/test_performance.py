"""
Performance benchmarks and tests for the ServiceContainer.

Tests ensure that dependency injection overhead is minimal and
service resolution performance meets application requirements.
"""

import time
import pytest
from statistics import mean, stdev
from typing import List

from promptbin.core.container import ServiceContainer


class TestPerformance:
    """Performance benchmarks for ServiceContainer operations."""

    def setup_method(self):
        """Set up fresh container for each test."""
        self.container = ServiceContainer()

    def test_single_service_resolution_performance(self):
        """Benchmark single service resolution speed."""

        class TestService:
            def __init__(self):
                self.value = "test"

        # Register service
        self.container.register_singleton(TestService, lambda c: TestService())

        # Warmup - resolve once to ensure singleton is cached
        self.container.resolve(TestService)

        # Benchmark resolution time (should use cached singleton)
        times = []
        iterations = 1000

        for _ in range(iterations):
            start = time.perf_counter()
            service = self.container.resolve(TestService)
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to milliseconds

            # Verify we got the service
            assert service.value == "test"

        avg_time = mean(times)
        max_time = max(times)

        # Performance requirements
        assert (
            avg_time < 0.1
        ), f"Average resolution time {avg_time:.3f}ms exceeds 0.1ms threshold"
        assert (
            max_time < 1.0
        ), f"Max resolution time {max_time:.3f}ms exceeds 1ms threshold"

        print(f"Single service resolution: avg={avg_time:.3f}ms, max={max_time:.3f}ms")

    def test_complex_dependency_graph_performance(self):
        """Benchmark resolution of complex dependency graphs."""

        # Create a complex dependency graph
        class DatabaseService:
            def __init__(self):
                self.connected = True

        class CacheService:
            def __init__(self):
                self.enabled = True

        class LoggingService:
            def __init__(self):
                self.level = "INFO"

        class ConfigService:
            def __init__(self):
                self.settings = {"debug": False}

        class RepositoryService:
            def __init__(self, db, cache, logger):
                self.db = db
                self.cache = cache
                self.logger = logger

        class BusinessService:
            def __init__(self, repo, config, logger):
                self.repo = repo
                self.config = config
                self.logger = logger

        class ApiService:
            def __init__(self, business, config, logger):
                self.business = business
                self.config = config
                self.logger = logger

        # Register all services
        self.container.register_singleton(DatabaseService, lambda c: DatabaseService())
        self.container.register_singleton(CacheService, lambda c: CacheService())
        self.container.register_singleton(LoggingService, lambda c: LoggingService())
        self.container.register_singleton(ConfigService, lambda c: ConfigService())
        self.container.register_singleton(
            RepositoryService,
            lambda c: RepositoryService(
                c.resolve(DatabaseService),
                c.resolve(CacheService),
                c.resolve(LoggingService),
            ),
        )
        self.container.register_singleton(
            BusinessService,
            lambda c: BusinessService(
                c.resolve(RepositoryService),
                c.resolve(ConfigService),
                c.resolve(LoggingService),
            ),
        )
        self.container.register_transient(
            ApiService,
            lambda c: ApiService(
                c.resolve(BusinessService),
                c.resolve(ConfigService),
                c.resolve(LoggingService),
            ),
        )

        # Warmup - resolve once to cache singletons
        self.container.resolve(ApiService)

        # Benchmark complex resolution
        times = []
        iterations = 100

        for _ in range(iterations):
            start = time.perf_counter()
            api_service = self.container.resolve(ApiService)
            end = time.perf_counter()
            times.append((end - start) * 1000)

            # Verify complete dependency graph was resolved
            assert api_service.business.repo.db.connected
            assert api_service.business.repo.cache.enabled
            assert api_service.config.settings["debug"] is False

        avg_time = mean(times)
        max_time = max(times)

        # Performance requirements for complex graph
        assert (
            avg_time < 0.5
        ), f"Average complex resolution time {avg_time:.3f}ms exceeds 0.5ms threshold"
        assert (
            max_time < 2.0
        ), f"Max complex resolution time {max_time:.3f}ms exceeds 2ms threshold"

        print(
            f"Complex dependency resolution: avg={avg_time:.3f}ms, max={max_time:.3f}ms"
        )

    def test_container_initialization_performance(self):
        """Benchmark container initialization and service registration."""

        class TestService:
            def __init__(self, value):
                self.value = value

        # Benchmark container creation and service registration
        times = []
        iterations = 1000

        for i in range(iterations):
            start = time.perf_counter()

            container = ServiceContainer()
            container.register_singleton(
                TestService, lambda c: TestService(f"value_{i}")
            )

            end = time.perf_counter()
            times.append((end - start) * 1000)

        avg_time = mean(times)
        max_time = max(times)

        # Performance requirements for initialization
        assert (
            avg_time < 0.05
        ), f"Average initialization time {avg_time:.3f}ms exceeds 0.05ms threshold"
        assert (
            max_time < 0.5
        ), f"Max initialization time {max_time:.3f}ms exceeds 0.5ms threshold"

        print(f"Container initialization: avg={avg_time:.3f}ms, max={max_time:.3f}ms")

    def test_transient_service_creation_overhead(self):
        """Benchmark overhead of transient service creation."""

        class TransientService:
            def __init__(self, value):
                self.value = value
                self.timestamp = time.time()

        # Register transient service
        self.container.register_transient(
            TransientService, lambda c: TransientService("transient")
        )

        # Benchmark transient service creation
        times = []
        iterations = 500

        for _ in range(iterations):
            start = time.perf_counter()
            service = self.container.resolve(TransientService)
            end = time.perf_counter()
            times.append((end - start) * 1000)

            assert service.value == "transient"

        avg_time = mean(times)
        max_time = max(times)

        # Transient services have more overhead but should still be fast
        assert (
            avg_time < 0.2
        ), f"Average transient creation time {avg_time:.3f}ms exceeds 0.2ms threshold"
        assert (
            max_time < 1.0
        ), f"Max transient creation time {max_time:.3f}ms exceeds 1ms threshold"

        print(f"Transient service creation: avg={avg_time:.3f}ms, max={max_time:.3f}ms")

    def test_large_service_graph_memory_efficiency(self):
        """Test memory efficiency with large number of services."""

        # Create many services to test memory usage
        num_services = 100

        # Base service class
        class BaseService:
            def __init__(self, service_id):
                self.service_id = service_id

        # Dynamically create service classes
        service_classes = []
        for i in range(num_services):
            service_class = type(f"Service{i}", (BaseService,), {})
            service_classes.append(service_class)

        # Register all services
        start_time = time.perf_counter()

        for i, service_class in enumerate(service_classes):
            self.container.register_singleton(
                service_class, lambda c, sid=i: service_class(sid)
            )

        registration_time = (time.perf_counter() - start_time) * 1000

        # Resolve all services
        start_time = time.perf_counter()

        resolved_services = []
        for service_class in service_classes:
            service = self.container.resolve(service_class)
            resolved_services.append(service)

        resolution_time = (time.perf_counter() - start_time) * 1000

        # Verify all services were created correctly
        assert len(resolved_services) == num_services
        for i, service in enumerate(resolved_services):
            assert service.service_id == i

        # Performance requirements for large graphs
        assert (
            registration_time < 50
        ), f"Registration time {registration_time:.1f}ms exceeds 50ms for {num_services} services"
        assert (
            resolution_time < 10
        ), f"Resolution time {resolution_time:.1f}ms exceeds 10ms for {num_services} services"

        print(
            f"Large service graph ({num_services} services): "
            f"registration={registration_time:.1f}ms, resolution={resolution_time:.1f}ms"
        )

    def test_concurrent_access_performance_baseline(self):
        """Baseline test for concurrent access patterns (single-threaded for now)."""

        class SharedService:
            def __init__(self):
                self.counter = 0

            def increment(self):
                self.counter += 1
                return self.counter

        # Register singleton service
        self.container.register_singleton(SharedService, lambda c: SharedService())

        # Simulate concurrent access patterns (sequential for baseline)
        times = []
        operations = 1000

        for _ in range(operations):
            start = time.perf_counter()
            service = self.container.resolve(SharedService)
            result = service.increment()
            end = time.perf_counter()
            times.append((end - start) * 1000)

        avg_time = mean(times)
        final_service = self.container.resolve(SharedService)

        # Verify singleton behavior
        assert final_service.counter == operations

        # Performance should remain consistent
        assert (
            avg_time < 0.1
        ), f"Average concurrent access time {avg_time:.3f}ms exceeds 0.1ms threshold"

        print(
            f"Concurrent access baseline: avg={avg_time:.3f}ms over {operations} operations"
        )


class TestBenchmarks:
    """Benchmark tests that can be run separately for performance analysis."""

    def setup_method(self):
        """Set up container for benchmarking."""
        self.container = ServiceContainer()

    @pytest.mark.skip(reason="Benchmarks skipped - run separately")
    def test_resolution_speed_benchmark(self):
        """Comprehensive resolution speed benchmark."""

        class Service:
            pass

        self.container.register_singleton(Service, lambda c: Service())

        # Run comprehensive benchmark
        iterations = 10000
        times = []

        # Warmup
        for _ in range(100):
            self.container.resolve(Service)

        # Actual benchmark
        for _ in range(iterations):
            start = time.perf_counter_ns()
            self.container.resolve(Service)
            end = time.perf_counter_ns()
            times.append((end - start) / 1000000)  # Convert to milliseconds

        # Statistics
        avg_time = mean(times)
        std_time = stdev(times)
        min_time = min(times)
        max_time = max(times)
        p95_time = sorted(times)[int(0.95 * len(times))]

        print(f"\nResolution Speed Benchmark ({iterations} iterations):")
        print(f"  Average: {avg_time:.4f}ms")
        print(f"  Std Dev: {std_time:.4f}ms")
        print(f"  Min:     {min_time:.4f}ms")
        print(f"  Max:     {max_time:.4f}ms")
        print(f"  95th %:  {p95_time:.4f}ms")

        # Assert performance criteria
        assert (
            avg_time < 0.01
        ), f"Average time {avg_time:.4f}ms exceeds target of 0.01ms"
        assert (
            p95_time < 0.05
        ), f"95th percentile {p95_time:.4f}ms exceeds target of 0.05ms"
