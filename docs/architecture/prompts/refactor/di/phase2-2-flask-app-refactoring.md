# Phase 2.2: Flask App Refactoring

## Context
Refactor the Flask application in `app.py` to eliminate global state management and implement proper dependency injection through an app factory pattern.

## Current Issues to Address

### Global State Problems (app.py:25-43)
```python
# Current problematic global state
share_manager = None  # Will be initialized after parsing args
prompt_manager = PromptManager()  # Default initialization
tunnel_manager = None  # Will be initialized with flask port

# Helper function to get share_manager
def get_share_manager():
    global share_manager
    if share_manager is None:
        share_manager = ShareManager()  # Use default path as fallback
    return share_manager
```

### Route Handler Dependencies
- Routes directly access global managers
- Hard to test individual routes with mocked services
- No clear service boundaries

## Requirements
- Remove all global variables (lines 25-43)
- Create `create_app(container)` factory function
- Update all route handlers to access services through dependency injection
- Maintain existing API contracts and behavior

## Implementation Guidelines

### App Factory Pattern
```python
def create_app(container: ServiceContainer) -> Flask:
    """Create Flask application with dependency injection"""
    app = Flask(__name__)
    
    # Resolve services from container
    prompt_manager = container.resolve(IPromptManager)
    share_manager = container.resolve(IShareManager)
    tunnel_manager = container.resolve(ITunnelManager)
    
    # Store services in app context for route access
    app.config['services'] = {
        'prompt_manager': prompt_manager,
        'share_manager': share_manager,
        'tunnel_manager': tunnel_manager
    }
    
    # Register blueprints/routes
    register_routes(app)
    return app
```

### Service Access in Routes
**Before:**
```python
@app.route('/')
def index():
    prompts = prompt_manager.list_prompts(category)
    stats = prompt_manager.get_stats()
    return render_template('index.html', prompts=prompts, stats=stats)
```

**After:**
```python
def index():
    services = current_app.config['services']
    prompt_manager = services['prompt_manager']
    prompts = prompt_manager.list_prompts(category)
    stats = prompt_manager.get_stats()
    return render_template('index.html', prompts=prompts, stats=stats)
```

### Route Registration Strategy
- Extract route definitions into separate functions
- Pass services as parameters to route registration
- Consider Flask blueprints for better organization

### Testing Requirements
- Flask app factory tests with different container configurations
- Route handler tests with mocked services
- Integration tests for full request/response cycles
- Global state elimination verification tests
- Flask test client integration with DI container

## Specific Routes to Refactor

### Core Routes
- `/` (index) - Uses prompt_manager
- `/view/<prompt_id>` - Uses prompt_manager
- `/edit/<prompt_id>` - Uses prompt_manager
- `/create` - Uses prompt_manager

### API Routes
- `/api/prompts` (POST/PUT/DELETE) - Uses prompt_manager
- `/api/search` - Uses prompt_manager
- `/api/share/<prompt_id>` - Uses share_manager, tunnel_manager
- `/api/tunnel/*` - Uses tunnel_manager

### Health/Status Routes
- `/health` - Uses prompt_manager, tunnel_manager
- `/mcp-status` - Configuration access

## Migration Strategy
1. **Create app factory alongside existing global approach**
2. **Update main() function to use factory when container is available**
3. **Gradually migrate routes to use services from app context**
4. **Remove global variables once all routes are migrated**
5. **Add deprecation warnings for old global access patterns**

## Success Criteria
- No global service variables in app.py
- All routes access services through dependency injection
- App factory creates fully configured Flask application
- Existing API behavior preserved
- Comprehensive test coverage for all routes with mocked services