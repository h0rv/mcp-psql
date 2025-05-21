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

Run in dev mode:

```bash
poe mcp-dev
```

Install to Claude Desktop:

```bash
poe install-claude-desktop
```
