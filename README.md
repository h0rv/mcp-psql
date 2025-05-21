# mcp-psql

Based off of the official TypeScript implementation server: https://github.com/modelcontextprotocol/servers/tree/main/src/postgres

## Setup

Add your database URI

```bash
cp .env.example .env
$EDITOR .env
```

Run in dev mode:

```bash
source .env
uv run mcp dev server.py
```

Install to Claude Desktop:

```bash
uv run mcp install --editable --env-file .env server.py
```
