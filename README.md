# mcp-calculator

Save as requirements.txt:

mcp>=0.5.0
openai>=1.3.0
python-dotenv>=1.0.0
Install with:
pip install -r requirements.txt


.ENV.EXAMPLE:

OPENAI_API_KEY=sk-proj-... #OpenAI API Key (get from https://platform.openai.com/api-keys)
OPENAI_MODEL=gpt-4o #Optional: Choose model (default: gpt-4o-mini)
DEBUG=false #Optional: Debug mode


Commands:

Start server:   python calculator_mcp_server.py
Start client:   python calculator_mcp_client.py ./calculator_mcp_server.py
