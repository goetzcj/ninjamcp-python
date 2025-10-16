#!/usr/bin/env python3
"""
Entry point for running NinjaRMM MCP Server as a module.

This allows the server to be started with:
    python -m ninjarmm_mcp

This is particularly useful for:
- CrewAI integration
- Docker containers
- Direct module execution
- Development and testing
"""

import asyncio
import sys
from .server import main

def run_main():
    """
    Synchronous wrapper for the async main function.
    
    This function handles the asyncio event loop setup and ensures
    proper cleanup when the server is terminated.
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_main()
