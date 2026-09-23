# yugabytedb-mcp-server

Read-only MCP server for a YugabyteDB database, via its PostgreSQL-compatible YSQL API.

## Tools

- `list_schemas()` — non-system schemas
- `list_tables(schema="public")` — tables in a schema
- `describe_table(table, schema="public")` — column names, types, nullability, defaults
- `execute_sql(query)` — run a `SELECT` statement over a read-only connection (only `SELECT` is permitted)

## Setup

```bash
cd servers/yugabytedb
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

| Env var | Default |
|---|---|
| `YUGABYTE_HOST` | `127.0.0.1` |
| `YUGABYTE_PORT` | `5433` (YSQL port) |
| `YUGABYTE_DATABASE` | `yugabyte` |
| `YUGABYTE_USER` | `yugabyte` |
| `YUGABYTE_PASSWORD` | *(empty)* |

## Add to an MCP client

```json
{
  "mcpServers": {
    "yugabytedb": {
      "command": "/absolute/path/to/servers/yugabytedb/.venv/bin/python",
      "args": ["/absolute/path/to/servers/yugabytedb/server.py"],
      "env": {
        "YUGABYTE_HOST": "127.0.0.1",
        "YUGABYTE_DATABASE": "yugabyte",
        "YUGABYTE_USER": "yugabyte",
        "YUGABYTE_PASSWORD": "yugabyte"
      }
    }
  }
}
```
