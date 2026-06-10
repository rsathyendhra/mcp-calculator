"""
Simple Calculator MCP Server
=============================

This MCP server exposes basic math operations as tools that Claude can call.

Run:
    python calculator_server.py
"""

import asyncio
from mcp.server.fastmcp import FastMCP

# Create MCP server instance
mcp = FastMCP("calculator")


# ============================================================================
# Define tools that MCP will expose
# ============================================================================

@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together"""
    return a + b


@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract b from a"""
    return a - b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers"""
    return a * b


@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide a by b"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


@mcp.tool()
def power(base: float, exponent: float) -> float:
    """Raise base to the power of exponent"""
    return base ** exponent


@mcp.tool()
def square_root(number: float) -> float:
    """Calculate the square root of a number"""
    if number < 0:
        raise ValueError("Cannot calculate square root of negative number")
    return number ** 0.5


# ============================================================================
# Run the server
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 Calculator MCP Server")
    print("=" * 60)
    print("\nAvailable tools:")
    print("  • add(a, b) - Add two numbers")
    print("  • subtract(a, b) - Subtract b from a")
    print("  • multiply(a, b) - Multiply two numbers")
    print("  • divide(a, b) - Divide a by b")
    print("  • power(base, exponent) - Raise base to power")
    print("  • square_root(number) - Calculate square root")
    print("\nStarting server on stdio...")
    print("=" * 60)
    print("\n✅ Server running. Connect your client to use these tools.\n")
    
    # Run server using stdio transport
    mcp.run(transport="stdio")
