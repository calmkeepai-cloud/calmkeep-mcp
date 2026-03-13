# Calmkeep MCP Connector

This repository provides an MCP server that routes prompts through the Calmkeep runtime.

## Installation

Clone the repository:

git clone https://github.com/calmkeepai-cloud/calmkeep-mcp
cd calmkeep-mcp

Install dependencies:

pip install -r requirements.txt

## Configure Environment

Create a `.env` file:

CALMKEEP_URL=https://your-calmkeep-modal-url.modal.run
CALMKEEP_API_KEY=your_calmkeep_key
ANTHROPIC_API_KEY=your_anthropic_key

## Run MCP Server

python mcp_server.py

This exposes the tool:

calmkeep_chat(prompt)




----------------------------------
Note: This repository ignores `node_modules/` in version control. If your environment requires Node dependencies, run `npm install` after cloning to regenerate them locally.
