# Phase 1.3: Service Interfaces

## Context
Define abstract base classes (interfaces) for all major PromptBin services to enable dependency injection, improve testability, and establish clear service contracts.

## Requirements
- Create `core/interfaces/` directory with interface definitions
- Define contracts for `IPromptManager`, `IShareManager`, `ITunnelManager`, `IFlaskManager`
- Enable mock implementations for testing
- Ensure all current functionality is captured in interfaces

## Current Services to Abstract

### PromptManager (prompt_manager.py)
Key methods to include in `IPromptManager`:
- `save_prompt(data, prompt_id=None) -> str`
- `get_prompt(prompt_id) -> Optional[Dict]`
- `list_prompts(category=None) -> List[Dict]`
- `delete_prompt(prompt_id) -> bool`
- `search_prompts(query, category=None) -> List[Dict]`
- `get_stats() -> Dict`

### ShareManager (share_manager.py)
Key methods to include in `IShareManager`:
- `create_share_token(prompt_id, expires_in_hours=None) -> str`
- `validate_share_token(token) -> Optional[str]`
- `get_share_info(token) -> Optional[Dict]`
- `revoke_share_token(token) -> bool`
- `list_shares_for_prompt(prompt_id) -> List[Dict]`
- `get_stats() -> Dict`

### TunnelManager (tunnel_manager.py)
Key methods to include in `ITunnelManager`:
- `start_tunnel(client_ip) -> Dict[str, Any]`
- `stop_tunnel() -> Dict[str, Any]`
- `get_status() -> Dict[str, Any]`
- `get_tunnel_url() -> Optional[str]`
- `is_tunnel_active() -> bool`
- `check_cli_available() -> tuple[bool, str]`
- `check_authentication() -> tuple[bool, str]`

### FlaskManager (flask_manager.py)
Key methods to include in `IFlaskManager`:
- `start_flask() -> None`
- `stop_flask() -> None`
- `restart_flask() -> None`
- `is_healthy() -> bool`
- `flask_status() -> Dict[str, Any]`

## Implementation Guidelines

### Interface Design Principles
1. **Method Signatures**: Match existing implementations exactly
2. **Return Types**: Use proper type hints for all methods
3. **Documentation**: Comprehensive docstrings for all interface methods
4. **Error Handling**: Define expected exceptions in interface contracts
5. **Async Support**: Mark async methods appropriately

### Directory Structure
```
core/interfaces/
├── __init__.py
├── prompt_manager.py      # IPromptManager
├── share_manager.py       # IShareManager  
├── tunnel_manager.py      # ITunnelManager
└── flask_manager.py       # IFlaskManager
```

### Example Interface
```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

class IPromptManager(ABC):
    @abstractmethod
    def save_prompt(self, data: Dict[str, Any], prompt_id: Optional[str] = None) -> str:
        """Save a prompt to storage"""
        pass
    
    @abstractmethod
    def get_prompt(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a prompt by ID"""
        pass
```

### Testing Requirements
- Interface compliance tests for all implementations
- Mock service implementations for testing
- Contract verification tests
- Interface method signature validation

## Integration Points
- Update existing service classes to implement these interfaces
- Use interfaces for type hints in dependency injection
- Enable easy swapping of implementations (e.g., different storage backends)

## Success Criteria
- All major services have well-defined interfaces
- Existing implementations satisfy interface contracts
- Mock implementations available for all interfaces
- Clear separation between interface and implementation
- Enhanced testability through dependency injection