# Phase 2: Implement Core MCP Protocol

## Overview
Implement the Model Context Protocol server interface and core endpoint handlers that allow AI tools like Claude to access PromptBin prompts via the MCP protocol.

## Prerequisites
- Phase 1 completed: MCP dependencies installed and basic server structure created
- MCP Python SDK integrated and working
- PromptManager integration established

## Requirements

### 1. MCP Server Interface Implementation
Implement the standard MCP server interface based on the chosen MCP library:

- **Protocol initialization**: Handle MCP handshake and capability negotiation
- **Message routing**: Route incoming MCP requests to appropriate handlers
- **Response formatting**: Format responses according to MCP protocol specifications
- **Error handling**: Proper MCP error codes and messages

### 2. Core MCP Endpoint Handlers

#### `list_prompts()` Handler
- **Purpose**: Return all available prompts with metadata
- **Integration**: Use `PromptManager.list_prompts()` 
- **Response format**:
  ```json
  {
    "prompts": [
      {
        "id": "prompt_id",
        "title": "Prompt Title",
        "category": "coding",
        "description": "Brief description",
        "created_at": "2024-01-01T10:00:00Z",
        "tags": ["tag1", "tag2"]
      }
    ],
    "total_count": 42
  }
  ```

#### `get_prompt(prompt_id)` Handler  
- **Purpose**: Retrieve specific prompt content by ID
- **Integration**: Use `PromptManager.get_prompt(prompt_id)`
- **Response format**:
  ```json
  {
    "id": "prompt_id",
    "title": "Prompt Title", 
    "content": "Full prompt content with {{variables}}",
    "category": "coding",
    "description": "Description",
    "tags": ["tag1", "tag2"],
    "metadata": {
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z",
      "word_count": 150,
      "template_variables": ["variable1", "variable2"]
    }
  }
  ```

#### `search_prompts(query)` Handler
- **Purpose**: Search prompts by content, title, tags, or description
- **Integration**: Use `PromptManager.search_prompts(query)`
- **Support parameters**: 
  - `query`: Search string
  - `category`: Optional category filter
  - `limit`: Optional result limit
- **Response**: Array of matching prompts with relevance scoring

### 3. Protocol URL Support
Implement support for `mcp://promptbin/get-prompt/{prompt-name}` format:

- **Name resolution**: Map prompt names to IDs
  - Use prompt title as name (with sanitization)
  - Handle name conflicts with unique suffixes
  - Support both ID and name-based access

- **URL routing**: Parse and route protocol URLs to appropriate handlers
- **Error handling**: Clear errors for invalid names/IDs

### 4. Enhanced Response Features

#### Template Variable Analysis
- **Extract variables**: Parse `{{variable}}` patterns from prompt content
- **Variable metadata**: Include variable names and count in responses
- **Usage hints**: Provide context for template variable usage

#### Content Statistics  
- **Word count**: Calculate and include word counts
- **Token estimation**: Provide token count estimates (words × 1.3)
- **Content analysis**: Basic content metrics for AI tools

### 5. Error Handling & Validation
- **Input validation**: Validate all incoming parameters
- **MCP error codes**: Use proper MCP protocol error responses
- **Graceful degradation**: Handle PromptManager errors gracefully
- **Logging**: Comprehensive logging for debugging and monitoring

## Implementation Details

### MCP Message Handling Structure
```python
class PromptBinMCPServer:
    async def handle_list_prompts(self, params):
        # Implementation for listing prompts
        
    async def handle_get_prompt(self, params):  
        # Implementation for getting single prompt
        
    async def handle_search_prompts(self, params):
        # Implementation for searching prompts
        
    def _format_prompt_response(self, prompt):
        # Helper to format prompt data for MCP response
        
    def _extract_template_variables(self, content):
        # Helper to extract {{variables}} from content
```

### Protocol URL Parsing
```python
def parse_protocol_url(self, url):
    # Parse mcp://promptbin/get-prompt/{name-or-id}
    # Return action and parameters
    
def resolve_prompt_name(self, name):
    # Convert prompt name to ID
    # Handle conflicts and sanitization
```

## Deliverables
1. Complete MCP protocol implementation with message handling
2. Three core endpoint handlers (`list_prompts`, `get_prompt`, `search_prompts`)
3. Protocol URL parsing and routing system
4. Template variable extraction and analysis
5. Comprehensive error handling and validation
6. Response formatting and content statistics

## Testing Requirements
- Test MCP protocol handshake and initialization
- Verify all endpoint handlers work with existing prompts
- Test protocol URL parsing and name resolution
- Validate error handling for invalid requests
- Confirm response formats match MCP specifications

## Success Criteria
- AI tools can successfully connect to MCP server
- All three core endpoints return properly formatted responses
- Protocol URLs resolve correctly to prompt content
- Error responses follow MCP standards
- Template variables are correctly identified and reported
- Integration with existing PromptManager works seamlessly

## Notes
- Focus on MCP protocol compliance - study the specification carefully
- Ensure responses are optimized for AI tool consumption
- Consider caching frequently accessed prompts for performance
- Document any protocol-specific design decisions
- Test with actual MCP-compatible AI tools if possible