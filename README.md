# mcp-psql

Based off of the official TypeScript implementation server: https://github.com/modelcontextprotocol/servers/tree/main/src/postgres

## Setup

Install deps

```bash
uv sync --frozen --all-groups
```

Add your Postgres database URI:

```bash
cp .env.example .env
$EDITOR .env
```

## Running

### Dev Mode (stdio)

```bash
poe mcp-dev
```

### Stdio

Install to Claude Desktop:

```bash
poe install-claude-desktop
```

Add to other clients:

```json
{
  "mcpServers": {
    "psql": {
      "command": "/opt/homebrew/bin/uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "--with-editable",
        "/Users/robby/projects/mcp-psql",
        "mcp",
        "run",
        "/Users/robby/projects/mcp-psql/server.py"
      ],
      "env": {
        "DATABASE_URI": "postgresql://username:password@localhost/my-db"
      }
    }
  }
}
```

### SSE

Run:

```bash
uv run --env-file .env server.py --transport sse
```

Add to client config:

```json
{
  "mcpServers": {
    "psql": {
      "url": "http://localhost:8000/sse",
    }
  }
}
```
