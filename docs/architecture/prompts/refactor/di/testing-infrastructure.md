# Testing Infrastructure for Dependency Injection

## Context
Comprehensive testing strategy and infrastructure to support the dependency injection refactoring, ensuring reliability, maintainability, and regression prevention.

## Test Organization Structure

### Directory Layout
```
tests/
├── unit/                    # Unit tests with mocked dependencies
│   ├── core/               # DI infrastructure tests
│   │   ├── test_container.py
│   │   ├── test_config.py
│   │   └── test_interfaces.py
│   ├── services/           # Individual service tests
│   │   ├── test_prompt_manager.py
│   │   ├── test_share_manager.py
│   │   ├── test_tunnel_manager.py
│   │   └── test_flask_manager.py
│   └── web/                # Flask app tests
│       ├── test_app_factory.py
│       └── test_routes.py
├── integration/            # Cross-service integration tests
│   ├── test_service_integration.py
│   ├── test_mcp_integration.py
│   └── test_cli_integration.py
├── e2e/                    # End-to-end application tests
│   ├── test_web_interface.py
│   ├── test_mcp_protocol.py
│   └── test_full_workflow.py
├── fixtures/               # Test data and utilities
│   ├── __init__.py
│   ├── sample_data.py
│   ├── mock_services.py
│   └── test_containers.py
└── conftest.py             # Pytest configuration and shared fixtures
```

## Core Testing Infrastructure

### Base Test Classes
```python
# tests/fixtures/base_test.py
import pytest
from unittest.mock import Mock
from core.container import ServiceContainer
from core.config import PromptBinConfig
from core.interfaces import IPromptManager, IShareManager

class BaseContainerTest:
    """Base class for tests requiring DI container"""
    
    @pytest.fixture
    def container(self):
        return ServiceContainer()
    
    @pytest.fixture
    def test_config(self):
        return PromptBinConfig(
            flask_host="127.0.0.1",
            flask_port=5001,
            data_dir="/tmp/test-promptbin-data",
            log_level="DEBUG"
        )
    
    @pytest.fixture
    def mock_prompt_manager(self):
        mock = Mock(spec=IPromptManager)
        mock.list_prompts.return_value = []
        mock.get_stats.return_value = {"total_prompts": 0}
        return mock

class BaseServiceTest(BaseContainerTest):
    """Base class for service-specific tests"""
    
    @pytest.fixture
    def configured_container(self, container, test_config, mock_services):
        """Container with all mock services registered"""
        container.register_singleton(PromptBinConfig, lambda: test_config)
        for interface, mock_service in mock_services.items():
            container.register_singleton(interface, lambda s=mock_service: s)
        return container
```

### Mock Service Implementations
```python
# tests/fixtures/mock_services.py
from typing import Dict, List, Optional, Any
from core.interfaces import IPromptManager, IShareManager, ITunnelManager

class MockPromptManager(IPromptManager):
    """Mock implementation for testing"""
    
    def __init__(self):
        self.prompts = {}
        self.next_id = 1
    
    def save_prompt(self, data: Dict[str, Any], prompt_id: Optional[str] = None) -> str:
        if prompt_id is None:
            prompt_id = f"test_prompt_{self.next_id}"
            self.next_id += 1
        
        self.prompts[prompt_id] = {
            "id": prompt_id,
            "title": data["title"],
            "content": data["content"],
            "category": data["category"]
        }
        return prompt_id
    
    def get_prompt(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        return self.prompts.get(prompt_id)
    
    def list_prompts(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        prompts = list(self.prompts.values())
        if category:
            prompts = [p for p in prompts if p.get("category") == category]
        return prompts

class MockShareManager(IShareManager):
    """Mock implementation for testing"""
    
    def __init__(self):
        self.shares = {}
    
    def create_share_token(self, prompt_id: str, expires_in_hours: Optional[int] = None) -> str:
        token = f"share_token_{len(self.shares)}"
        self.shares[token] = {"prompt_id": prompt_id, "expires_in_hours": expires_in_hours}
        return token
```

### Test Data Factory
```python
# tests/fixtures/sample_data.py
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class PromptTestData:
    """Factory for test prompt data"""
    
    @staticmethod
    def coding_prompt() -> Dict[str, Any]:
        return {
            "title": "Test Coding Prompt",
            "content": "Write a function that {{task}}",
            "category": "coding",
            "description": "A test prompt for coding tasks",
            "tags": ["test", "coding"]
        }
    
    @staticmethod
    def writing_prompt() -> Dict[str, Any]:
        return {
            "title": "Test Writing Prompt", 
            "content": "Write about {{topic}} in {{style}} style",
            "category": "writing",
            "description": "A test prompt for writing tasks",
            "tags": ["test", "writing"]
        }
    
    @staticmethod
    def invalid_prompt() -> Dict[str, Any]:
        return {
            "content": "Missing title and category"
        }
```

## Unit Testing Strategies

### Container Testing
```python
# tests/unit/core/test_container.py
import pytest
from core.container import ServiceContainer, ServiceResolutionError, CircularDependencyError

class TestServiceContainer:
    
    def test_register_and_resolve_singleton(self, container):
        """Test singleton service registration and resolution"""
        
        class TestService:
            pass
        
        instance = TestService()
        container.register_singleton(TestService, lambda: instance)
        
        resolved1 = container.resolve(TestService)
        resolved2 = container.resolve(TestService)
        
        assert resolved1 is instance
        assert resolved2 is instance  # Same instance (singleton)
    
    def test_register_and_resolve_transient(self, container):
        """Test transient service registration and resolution"""
        
        class TestService:
            pass
        
        container.register_transient(TestService, lambda: TestService())
        
        resolved1 = container.resolve(TestService)
        resolved2 = container.resolve(TestService)
        
        assert isinstance(resolved1, TestService)
        assert isinstance(resolved2, TestService)
        assert resolved1 is not resolved2  # Different instances (transient)
    
    def test_circular_dependency_detection(self, container):
        """Test circular dependency detection"""
        
        class ServiceA:
            def __init__(self, service_b):
                self.service_b = service_b
        
        class ServiceB:
            def __init__(self, service_a):
                self.service_a = service_a
        
        container.register_singleton(ServiceA, lambda: ServiceA(container.resolve(ServiceB)))
        container.register_singleton(ServiceB, lambda: ServiceB(container.resolve(ServiceA)))
        
        with pytest.raises(CircularDependencyError) as exc_info:
            container.resolve(ServiceA)
        
        assert "ServiceA" in str(exc_info.value)
        assert "ServiceB" in str(exc_info.value)
```

### Service Testing with DI
```python
# tests/unit/services/test_prompt_manager.py
import pytest
from prompt_manager import PromptManager
from core.config import PromptBinConfig
from tests.fixtures.sample_data import PromptTestData

class TestPromptManagerWithDI:
    
    @pytest.fixture
    def test_config(self, tmp_path):
        """Configuration pointing to temporary directory"""
        return PromptBinConfig(data_dir=str(tmp_path / "test_data"))
    
    @pytest.fixture
    def prompt_manager(self, test_config):
        """PromptManager instance with test configuration"""
        return PromptManager(test_config)
    
    def test_save_and_retrieve_prompt(self, prompt_manager):
        """Test saving and retrieving prompts"""
        prompt_data = PromptTestData.coding_prompt()
        
        prompt_id = prompt_manager.save_prompt(prompt_data)
        retrieved = prompt_manager.get_prompt(prompt_id)
        
        assert retrieved is not None
        assert retrieved["title"] == prompt_data["title"]
        assert retrieved["category"] == prompt_data["category"]
    
    def test_list_prompts_by_category(self, prompt_manager):
        """Test category filtering"""
        coding_prompt = PromptTestData.coding_prompt()
        writing_prompt = PromptTestData.writing_prompt()
        
        prompt_manager.save_prompt(coding_prompt)
        prompt_manager.save_prompt(writing_prompt)
        
        coding_prompts = prompt_manager.list_prompts("coding")
        writing_prompts = prompt_manager.list_prompts("writing")
        
        assert len(coding_prompts) == 1
        assert len(writing_prompts) == 1
        assert coding_prompts[0]["category"] == "coding"
        assert writing_prompts[0]["category"] == "writing"
```

## Integration Testing

### Service Integration Tests
```python
# tests/integration/test_service_integration.py
import pytest
from core.container import ServiceContainer
from core.config import PromptBinConfig
from prompt_manager import PromptManager
from share_manager import ShareManager

class TestServiceIntegration:
    
    @pytest.fixture
    def integrated_container(self, tmp_path):
        """Container with real services for integration testing"""
        container = ServiceContainer()
        
        config = PromptBinConfig(data_dir=str(tmp_path / "integration_data"))
        
        container.register_singleton(PromptBinConfig, lambda: config)
        container.register_singleton(IPromptManager, lambda: PromptManager(config))
        container.register_singleton(IShareManager, lambda: ShareManager(config))
        
        return container
    
    def test_share_existing_prompt(self, integrated_container):
        """Test sharing a prompt created through PromptManager"""
        prompt_manager = integrated_container.resolve(IPromptManager)
        share_manager = integrated_container.resolve(IShareManager)
        
        # Create a prompt
        prompt_data = {"title": "Test", "content": "Content", "category": "coding"}
        prompt_id = prompt_manager.save_prompt(prompt_data)
        
        # Share the prompt
        token = share_manager.create_share_token(prompt_id)
        
        # Validate the share
        validated_id = share_manager.validate_share_token(token)
        assert validated_id == prompt_id
        
        # Verify the prompt can be retrieved
        retrieved = prompt_manager.get_prompt(prompt_id)
        assert retrieved is not None
```

## Flask Testing with DI

### App Factory Testing
```python
# tests/unit/web/test_app_factory.py
import pytest
from flask.testing import FlaskClient
from app import create_app
from tests.fixtures.mock_services import MockPromptManager, MockShareManager

class TestAppFactory:
    
    @pytest.fixture
    def app_with_mocks(self, container, test_config):
        """Flask app with mocked services"""
        container.register_singleton(PromptBinConfig, lambda: test_config)
        container.register_singleton(IPromptManager, lambda: MockPromptManager())
        container.register_singleton(IShareManager, lambda: MockShareManager())
        
        return create_app(container)
    
    @pytest.fixture
    def client(self, app_with_mocks) -> FlaskClient:
        """Flask test client"""
        return app_with_mocks.test_client()
    
    def test_index_route_with_mocked_services(self, client):
        """Test index route uses injected services"""
        response = client.get('/')
        
        assert response.status_code == 200
        # Verify template rendered with mocked data
    
    def test_api_endpoints_with_mocked_services(self, client):
        """Test API endpoints work with mocked services"""
        prompt_data = {
            "title": "Test Prompt",
            "content": "Test content", 
            "category": "coding"
        }
        
        response = client.post('/api/prompts', json=prompt_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
```

## Performance Testing

### Benchmark Tests
```python
# tests/performance/test_container_performance.py
import pytest
import time
from core.container import ServiceContainer

class TestContainerPerformance:
    
    @pytest.mark.benchmark
    def test_service_resolution_performance(self, benchmark):
        """Benchmark service resolution speed"""
        container = ServiceContainer()
        
        class TestService:
            pass
        
        container.register_singleton(TestService, lambda: TestService())
        
        # Benchmark resolution time
        result = benchmark(container.resolve, TestService)
        
        assert isinstance(result, TestService)
        # Ensure resolution is fast enough for application startup
        assert benchmark.stats['mean'] < 0.001  # Less than 1ms
```

## Test Configuration

### pytest Configuration
```python
# conftest.py
import pytest
import tempfile
import shutil
from pathlib import Path

@pytest.fixture(scope="session")
def test_data_dir():
    """Session-scoped temporary directory for test data"""
    temp_dir = tempfile.mkdtemp(prefix="promptbin_test_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

@pytest.fixture(autouse=True)
def isolate_tests(monkeypatch, test_data_dir):
    """Isolate tests by using temporary directories"""
    # Ensure each test gets a clean data directory
    test_dir = test_data_dir / "current_test"
    test_dir.mkdir(exist_ok=True)
    
    # Clean up after each test
    yield
    
    if test_dir.exists():
        shutil.rmtree(test_dir)

# Coverage configuration
pytest_plugins = ["pytest_cov"]

# Markers for different test types
pytest.ini = """
[tool:pytest]
markers =
    unit: Unit tests with mocked dependencies
    integration: Integration tests with real services
    e2e: End-to-end tests
    benchmark: Performance benchmark tests
    slow: Tests that take longer to run
"""
```

## Success Criteria

### Coverage Requirements
- **Container & Config**: 100% code coverage
- **Service Classes**: 90%+ code coverage  
- **Integration Paths**: All major workflows tested
- **Error Scenarios**: All exception paths tested

### Performance Benchmarks
- Service resolution: < 1ms average
- Container initialization: < 100ms
- Full application startup: < 5s

### Test Quality Metrics
- All tests must be deterministic (no flaky tests)
- Clear test names describing behavior
- Comprehensive assertion messages
- Isolated tests with no interdependencies