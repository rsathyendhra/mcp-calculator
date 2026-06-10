# mcp-calculator

Save as requirements.txt:
mcp>=0.5.0
openai>=1.3.0
python-dotenv>=1.0.0
Install with:
pip install -r requirements.txt


.ENV.EXAMPLE

#OpenAI API Key (get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-proj-...
#Optional: Choose model (default: gpt-4o-mini)
OPENAI_MODEL=gpt-4o
#Optional: Debug mode
DEBUG=false


Commands:
Start server:   python Calculator_MCP_Server.py
Start client:   python Calculator_MCP_Client.py ./Calculator_MCP_Server.py
