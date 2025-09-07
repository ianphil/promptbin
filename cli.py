#!/usr/bin/env python3
"""
PromptBin CLI - Unified command-line interface

Provides a single entry point that runs both MCP server and web interface by default,
with options to run individual components.
"""

import argparse
import asyncio
import logging
import os
import sys
import time
from pathlib import Path

def create_parser():
    """Create the argument parser for PromptBin CLI"""
    parser = argparse.ArgumentParser(
        description='PromptBin - MCP Server with Web Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  promptbin                    # Run both MCP server and web interface (default)
  promptbin --mcp              # Run only MCP server
  promptbin --web              # Run only web interface
  promptbin --port 8080        # Run on custom port
  promptbin --data-dir ~/my-prompts  # Use custom data directory
        """
    )
    
    # Mode selection (mutually exclusive)
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--both', 
        action='store_true', 
        default=True,
        help='Run both MCP server and web interface (default)'
    )
    mode_group.add_argument(
        '--mcp', 
        action='store_true',
        help='Run only MCP server'
    )
    mode_group.add_argument(
        '--web', 
        action='store_true',
        help='Run only web interface'
    )
    
    # Configuration options
    parser.add_argument(
        '--host', 
        default='127.0.0.1',
        help='Host to bind to (default: 127.0.0.1)'
    )
    parser.add_argument(
        '--port', 
        type=int, 
        default=5001,
        help='Port to run on (default: 5001)'
    )
    parser.add_argument(
        '--data-dir', 
        default=os.path.expanduser('~/promptbin-data'),
        help='Directory for prompt data (default: ~/promptbin-data)'
    )
    parser.add_argument(
        '--log-level', 
        default=os.environ.get('PROMPTBIN_LOG_LEVEL', 'INFO'),
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (default: INFO)'
    )
    
    # Version
    parser.add_argument(
        '--version', 
        action='version', 
        version='PromptBin 0.3.0'
    )
    
    return parser

def run_web_only(args):
    """Run only the web interface"""
    from app import main as app_main
    
    # Set up sys.argv for app.py's argument parser
    sys.argv = [
        'promptbin',
        '--host', args.host,
        '--port', str(args.port),
        '--mode', 'standalone',
        '--log-level', args.log_level,
        '--data-dir', args.data_dir
    ]
    
    print(f"🌐 Starting PromptBin web interface at http://{args.host}:{args.port}")
    app_main()

def run_mcp_only(args):
    """Run only the MCP server"""
    from mcp_server import main as mcp_main
    
    # Set environment variables for MCP server
    os.environ['PROMPTBIN_HOST'] = args.host
    os.environ['PROMPTBIN_PORT'] = str(args.port)
    os.environ['PROMPTBIN_DATA_DIR'] = args.data_dir
    os.environ['PROMPTBIN_LOG_LEVEL'] = args.log_level
    
    print("🤖 Starting PromptBin MCP server...")
    return mcp_main()

def run_both(args):
    """Run both MCP server and web interface (MCP server will launch Flask subprocess)"""
    from mcp_server import main as mcp_main
    
    # Set environment variables for MCP server (which will launch Flask subprocess)
    os.environ['PROMPTBIN_HOST'] = args.host
    os.environ['PROMPTBIN_PORT'] = str(args.port)
    os.environ['PROMPTBIN_DATA_DIR'] = args.data_dir
    os.environ['PROMPTBIN_LOG_LEVEL'] = args.log_level
    
    print("🚀 Starting PromptBin (MCP server + web interface)...")
    print(f"🤖 MCP server: Ready for AI tool connections")
    print(f"🌐 Web interface: Will be available at http://{args.host}:{args.port}")
    print("💡 Note: Web interface runs as a subprocess when in MCP mode")
    
    return mcp_main()

def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Determine which mode to run
    if args.mcp:
        mode = "mcp"
    elif args.web:
        mode = "web"
    else:
        mode = "both"  # Default
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        if mode == "web":
            run_web_only(args)
        elif mode == "mcp":
            return run_mcp_only(args)
        else:  # both
            return run_both(args)
    except KeyboardInterrupt:
        print("\n👋 PromptBin stopped")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())