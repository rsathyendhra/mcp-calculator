"""
Calculator MCP Client with OpenAI Integration
==============================================

This client connects to the Calculator MCP Server and uses OpenAI's GPT
to interpret user math requests and call the appropriate tools.

Requires:
    - OpenAI API key (from https://platform.openai.com/api-keys)
    - mcp, openai, python-dotenv packages

Run:
    python calculator_client_openai.py
"""

import asyncio
import sys
from typing import Optional
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class CalculatorMCPClient:
    """Client for the Calculator MCP Server using OpenAI GPT"""

    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.client = OpenAI()  # Uses OPENAI_API_KEY from env
        self.tools = []
        self.model = "gpt-4o-mini"  # Fast and capable for calculations

    async def connect_to_server(self, server_script_path: str):
        """
        Connect to the MCP Calculator Server
        
        Args:
            server_script_path: Path to calculator_server.py
        """
        try:
            # Create server parameters for stdio connection
            server_params = StdioServerParameters(
                command="python",
                args=[server_script_path]
            )
            
            print(f"🔗 Connecting to MCP server: {server_script_path}")
            
            # Connect using stdio
            read, write = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            
            # Create and initialize session
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            await self.session.initialize()
            
            # Get available tools
            tools_response = await self.session.list_tools()
            self.tools = tools_response.tools
            
            print(f"✅ Connected successfully!")
            print(f"📊 Available tools: {len(self.tools)}")
            for tool in self.tools:
                print(f"   • {tool.name}")
            
        except Exception as e:
            print(f"❌ Error connecting to server: {e}")
            raise

    def _format_tools_for_openai(self) -> list:
        """Convert MCP tools to OpenAI function calling format"""
        openai_tools = []
        
        for tool in self.tools:
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            }
            openai_tools.append(openai_tool)
        
        return openai_tools

    async def calculate(self, user_query: str) -> str:
        """
        Process a user's math query using OpenAI GPT and calculator tools
        
        Args:
            user_query: The user's math question or request
            
        Returns:
            GPT's response with the calculation result
        """
        if not self.session:
            raise RuntimeError("Not connected to server. Call connect_to_server first.")
        
        # Prepare tools for OpenAI API
        openai_tools = self._format_tools_for_openai()
        
        print(f"\n👤 You: {user_query}")
        
        # Initialize message history
        messages = [{"role": "user", "content": user_query}]
        
        # Keep processing while GPT uses tools
        iteration = 0
        max_iterations = 10  # Prevent infinite loops
        
        while iteration < max_iterations:
            iteration += 1
            
            # Send message to OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=openai_tools if openai_tools else None,
                temperature=0.7
            )
            
            # Check if GPT wants to use a tool
            tool_used = False
            
            # Process response choices
            for choice in response.choices:
                if choice.finish_reason == "tool_calls":
                    tool_used = True
                    
                    # Add assistant's response to messages
                    messages.append({
                        "role": "assistant",
                        "content": choice.message.content or "",
                        "tool_calls": choice.message.tool_calls
                    })
                    
                    # Process each tool call
                    tool_results = []
                    for tool_call in choice.message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_input = eval(tool_call.function.arguments)  # Parse JSON string
                        tool_use_id = tool_call.id
                        
                        print(f"   🔧 Using tool: {tool_name}")
                        print(f"   📥 Input: {tool_input}")
                        
                        # Call the tool on the MCP server
                        try:
                            result = await self.session.call_tool(tool_name, tool_input)
                            
                            # Extract result text
                            result_text = result.content[0].text if result.content else "No result"
                            
                            # Handle numeric results
                            try:
                                result_value = float(result_text)
                                print(f"   📤 Result: {result_value}")
                            except (ValueError, TypeError):
                                print(f"   📤 Result: {result_text}")
                            
                            tool_results.append({
                                "tool_call_id": tool_use_id,
                                "result": result_text
                            })
                            
                        except Exception as e:
                            error_msg = f"Error: {str(e)}"
                            print(f"   ❌ {error_msg}")
                            tool_results.append({
                                "tool_call_id": tool_use_id,
                                "result": error_msg
                            })
                    
                    # Add all tool results to messages
                    for tool_result in tool_results:
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_result["tool_call_id"],
                            "content": tool_result["result"]
                        })
                
                elif choice.finish_reason == "stop":
                    # GPT finished and didn't use tools
                    final_response = choice.message.content or "No response"
                    print(f"\n🤖 OpenAI: {final_response}")
                    return final_response
            
            # If tool was used, continue the loop to get GPT's next response
            if not tool_used:
                break
        
        return "Max iterations reached"

    async def interactive_mode(self):
        """
        Run an interactive loop where user can ask math questions
        """
        print("\n" + "=" * 60)
        print("💬 Calculator Chat with OpenAI (Interactive Mode)")
        print("=" * 60)
        print("\nTry asking things like:")
        print("  • What is 25 times 4?")
        print("  • Calculate the square root of 144")
        print("  • What's 100 divided by 4?")
        print("  • Multiply 7 by 8, then add 15")
        print("  • What is 2 to the power of 10?")
        print("\nType 'quit' or 'exit' to stop\n")
        
        while True:
            try:
                user_input = input("Enter a math question: ").strip()
                
                if user_input.lower() in ['quit', 'exit']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                await self.calculate(user_input)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def main():
    """Main entry point"""
    
    # Check if server path was provided
    if len(sys.argv) < 2:
        print("Usage: python calculator_client_openai.py <path_to_calculator_server.py>")
        print("\nExample:")
        print("  python calculator_client_openai.py ./calculator_server.py")
        print("\nMake sure calculator_server.py is running in a separate terminal:")
        print("  python calculator_server.py")
        print("\nAlso ensure OPENAI_API_KEY is set in .env or environment")
        sys.exit(1)
    
    server_path = sys.argv[1]
    client = CalculatorMCPClient()
    
    try:
        print("=" * 60)
        print("🧮 Calculator MCP App with OpenAI")
        print("=" * 60)
        print(f"Model: {client.model}")
        
        # Connect to server
        await client.connect_to_server(server_path)
        
        # Run interactive mode
        await client.interactive_mode()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
