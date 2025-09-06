#!/usr/bin/env python3
"""
PromptBin MCP Server

Model Context Protocol server implementation for PromptBin.
Provides AI tools access to prompts via the MCP protocol while managing
the Flask web interface lifecycle.
"""

import asyncio
import logging
import os
import re
import signal
import sys
from typing import Dict, Any, Optional, List
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from prompt_manager import PromptManager


class PromptBinMCPServer:
    """MCP server for PromptBin with Flask subprocess management"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the MCP server with configuration"""
        self.config = config or self._load_default_config()
        self.mcp = FastMCP("PromptBin")
        self.prompt_manager = PromptManager()
        self.flask_process = None
        self.is_running = False
        
        # Set up logging
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Register signal handlers for graceful shutdown
        self._setup_signal_handlers()
        
        # Register MCP protocol handlers
        self._register_mcp_handlers()
        
        self.logger.info("PromptBin MCP Server initialized")
        self.logger.debug(f"Configuration: {self._safe_config_log()}")
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration with environment variable overrides"""
        return {
            'mode': os.getenv('PROMPTBIN_MODE', 'mcp-managed'),
            'flask_port': int(os.getenv('PROMPTBIN_PORT', '5000')),
            'flask_host': os.getenv('PROMPTBIN_HOST', '127.0.0.1'),
            'log_level': os.getenv('PROMPTBIN_LOG_LEVEL', 'INFO'),
            'data_dir': os.getenv('PROMPTBIN_DATA_DIR', str(Path('prompts').absolute())),
            'health_check_interval': 30,
            'shutdown_timeout': 10,
        }
    
    def _setup_logging(self):
        """Configure structured logging"""
        log_level = getattr(logging, self.config['log_level'].upper(), logging.INFO)
        
        # Configure root logger
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # Set library log levels
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating shutdown...")
            asyncio.create_task(self.shutdown())
        
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, signal_handler)
        if hasattr(signal, 'SIGINT'):
            signal.signal(signal.SIGINT, signal_handler)
    
    def _safe_config_log(self) -> Dict[str, Any]:
        """Return configuration safe for logging (no sensitive data)"""
        safe_config = self.config.copy()
        # Remove any sensitive keys if they exist
        return safe_config
    
    def _extract_template_variables(self, content: str) -> List[str]:
        """Extract template variables from content using {{variable}} pattern"""
        if not content:
            return []
        
        # Find all {{variable}} patterns and extract variable names
        matches = re.findall(r'\{\{(\w+)\}\}', content)
        # Return unique variable names, preserving order
        return list(dict.fromkeys(matches))
    
    def _calculate_content_stats(self, content: str) -> Dict[str, Any]:
        """Calculate content statistics including word count and token estimation"""
        if not content:
            return {
                "word_count": 0,
                "token_count": 0,
                "template_variables": []
            }
        
        # Calculate word count (split on whitespace and count non-empty strings)
        words = [word for word in content.split() if word.strip()]
        word_count = len(words)
        
        # Token estimation using industry standard approximation
        token_count = int(word_count * 1.3)
        
        # Extract template variables
        template_variables = self._extract_template_variables(content)
        
        return {
            "word_count": word_count,
            "token_count": token_count,
            "template_variables": template_variables
        }
    
    def _format_prompt_for_mcp(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform PromptManager data to MCP-compliant format with enhanced metadata"""
        if not prompt_data:
            return {}
        
        # Calculate content statistics
        content_stats = self._calculate_content_stats(prompt_data.get('content', ''))
        
        return {
            "id": prompt_data.get('id', ''),
            "title": prompt_data.get('title', ''),
            "content": prompt_data.get('content', ''),
            "category": prompt_data.get('category', ''),
            "description": prompt_data.get('description', ''),
            "tags": prompt_data.get('tags', []),
            "metadata": {
                "created_at": prompt_data.get('created_at', ''),
                "updated_at": prompt_data.get('updated_at', ''),
                "word_count": content_stats["word_count"],
                "token_count": content_stats["token_count"],
                "template_variables": content_stats["template_variables"]
            }
        }
    
    def _resolve_prompt_name(self, name: str) -> Optional[str]:
        """Convert prompt name to ID, supporting both ID and sanitized title lookup"""
        if not name:
            return None
        
        # First, try direct ID lookup
        if self.prompt_manager.get_prompt(name):
            return name
        
        # If not found as ID, try name-based lookup
        all_prompts = self.prompt_manager.list_prompts()
        
        # Create sanitized name from title for comparison
        for prompt in all_prompts:
            title = prompt.get('title', '')
            if title:
                # Sanitize title: lowercase, replace spaces/special chars with dashes
                sanitized_title = re.sub(r'[^\w\s-]', '', title.lower())
                sanitized_title = re.sub(r'[\s_-]+', '-', sanitized_title).strip('-')
                
                if sanitized_title == name.lower():
                    return prompt.get('id')
        
        return None
    
    def _register_mcp_handlers(self):
        """Register MCP protocol handlers with FastMCP"""
        
        @self.mcp.resource("promptbin://list-prompts")
        def list_all_prompts() -> Dict[str, Any]:
            """List all available prompts with metadata"""
            try:
                prompts = self.prompt_manager.list_prompts()
                formatted_prompts = [self._format_prompt_for_mcp(p) for p in prompts]
                
                self.logger.debug(f"Listed {len(formatted_prompts)} prompts")
                return {
                    "prompts": formatted_prompts,
                    "total_count": len(formatted_prompts)
                }
            except Exception as e:
                self.logger.error(f"Error listing prompts: {e}")
                raise ValueError(f"Failed to list prompts: {str(e)}")
        
        @self.mcp.resource("promptbin://get-prompt/{prompt_id}")
        def get_single_prompt(prompt_id: str) -> Dict[str, Any]:
            """Get a single prompt by ID with full content and metadata"""
            try:
                # Resolve name to ID if needed
                resolved_id = self._resolve_prompt_name(prompt_id)
                if not resolved_id:
                    raise ValueError(f"Prompt not found: {prompt_id}")
                
                prompt = self.prompt_manager.get_prompt(resolved_id)
                if not prompt:
                    raise ValueError(f"Prompt not found: {prompt_id}")
                
                formatted_prompt = self._format_prompt_for_mcp(prompt)
                self.logger.debug(f"Retrieved prompt: {prompt_id}")
                return formatted_prompt
                
            except Exception as e:
                self.logger.error(f"Error getting prompt {prompt_id}: {e}")
                raise ValueError(f"Failed to get prompt {prompt_id}: {str(e)}")
        
        @self.mcp.tool()
        def search_prompts(query: str, category: Optional[str] = None, limit: Optional[int] = None) -> Dict[str, Any]:
            """Search prompts by content, title, tags, or description"""
            try:
                if not query or not query.strip():
                    raise ValueError("Search query cannot be empty")
                
                # Perform search using PromptManager
                results = self.prompt_manager.search_prompts(query.strip(), category)
                
                # Apply limit if specified
                if limit and limit > 0:
                    results = results[:limit]
                
                # Format results for MCP
                formatted_results = [self._format_prompt_for_mcp(p) for p in results]
                
                self.logger.debug(f"Search query '{query}' returned {len(formatted_results)} results")
                return {
                    "results": formatted_results,
                    "total_count": len(formatted_results),
                    "query": query,
                    "category_filter": category,
                    "limit_applied": limit
                }
                
            except Exception as e:
                self.logger.error(f"Error searching prompts with query '{query}': {e}")
                raise ValueError(f"Search failed: {str(e)}")
        
        # Additional resource for name-based access (protocol URL support)
        @self.mcp.resource("promptbin://get-prompt-by-name/{name}")
        def get_prompt_by_name(name: str) -> Dict[str, Any]:
            """Get a prompt by sanitized name (alternative to ID-based access)"""
            try:
                # This is an alias for get_single_prompt with explicit name resolution
                resolved_id = self._resolve_prompt_name(name)
                if not resolved_id:
                    # Try to find similar names for helpful error message
                    all_prompts = self.prompt_manager.list_prompts()
                    available_names = []
                    for p in all_prompts[:5]:  # Show first 5 as examples
                        title = p.get('title', '')
                        if title:
                            sanitized = re.sub(r'[^\w\s-]', '', title.lower())
                            sanitized = re.sub(r'[\s_-]+', '-', sanitized).strip('-')
                            available_names.append(sanitized)
                    
                    error_msg = f"Prompt '{name}' not found."
                    if available_names:
                        error_msg += f" Available names: {', '.join(available_names)}"
                    
                    raise ValueError(error_msg)
                
                prompt = self.prompt_manager.get_prompt(resolved_id)
                if not prompt:
                    raise ValueError(f"Prompt not found: {name}")
                
                formatted_prompt = self._format_prompt_for_mcp(prompt)
                self.logger.debug(f"Retrieved prompt by name: {name} -> {resolved_id}")
                return formatted_prompt
                
            except Exception as e:
                self.logger.error(f"Error getting prompt by name '{name}': {e}")
                raise ValueError(f"Failed to get prompt '{name}': {str(e)}")
        
        self.logger.info("MCP protocol handlers registered successfully")
    
    async def start(self):
        """Start the MCP server and Flask subprocess"""
        if self.is_running:
            self.logger.warning("Server is already running")
            return
        
        try:
            self.logger.info("Starting PromptBin MCP Server...")
            
            # Verify PromptManager is working
            prompts = self.prompt_manager.list_prompts()
            self.logger.info(f"PromptManager initialized - {len(prompts)} prompts available")
            
            # MCP protocol handlers already registered in __init__
            # Available endpoints:
            # - promptbin://list-prompts (resource)
            # - promptbin://get-prompt/{id} (resource)  
            # - search_prompts (tool)
            # - promptbin://get-prompt-by-name/{name} (resource)
            
            # TODO Phase 3: Start Flask subprocess
            # - Launch Flask app as subprocess
            # - Set up health monitoring
            # - Configure port management
            
            self.is_running = True
            self.logger.info("MCP Server started successfully")
            
            # Keep the server running
            while self.is_running:
                await asyncio.sleep(1)
                
        except Exception as e:
            self.logger.error(f"Error starting MCP server: {e}")
            raise
    
    async def shutdown(self):
        """Gracefully shutdown the MCP server and cleanup resources"""
        if not self.is_running:
            return
            
        self.logger.info("Shutting down PromptBin MCP Server...")
        self.is_running = False
        
        try:
            # TODO Phase 3: Stop Flask subprocess gracefully
            # - Send SIGTERM to Flask process
            # - Wait for clean termination
            # - Force kill if necessary
            
            self.logger.info("MCP Server shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            raise


async def main():
    """Main entry point for the MCP server"""
    server = None
    try:
        server = PromptBinMCPServer()
        await server.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        return 1
    finally:
        if server:
            await server.shutdown()
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)