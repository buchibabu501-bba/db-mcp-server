# db-mcp-server

MCP (Model Context Protocol) servers for talking to different database platforms from an MCP-compatible client (Claude Desktop, Claude Code, etc.).

Each server lives in its own directory under `servers/`, installs independently, and exposes a small, deliberately **read-only** toolset: list schemas/keyspaces, list tables, describe a table's columns, and run a `SELECT`-only query.

## Servers

| Database | Status | Path |
|---|---|---|
| Cassandra | done | [`servers/cassandra`](servers/cassandra) |
| YugabyteDB (YSQL) | done | [`servers/yugabytedb`](servers/yugabytedb) |
| PostgreSQL | planned | — |
| MySQL | planned | — |

## Why read-only?

These tools let an LLM explore and query a database on your behalf. Restricting every server to `SELECT`-only — and, where the driver supports it, a read-only session — means a misbehaving or manipulated prompt can't modify or delete your data through these tools.

## Usage

Each server's own README covers its setup and environment variables. In general, add it to your MCP client's config (e.g. Claude Desktop's `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "cassandra": {
      "command": "/absolute/path/to/servers/cassandra/.venv/bin/python",
      "args": ["/absolute/path/to/servers/cassandra/server.py"],
      "env": {
        "CASSANDRA_CONTACT_POINTS": "127.0.0.1",
        "CASSANDRA_LOCAL_DATACENTER": "datacenter1"
      }
    },
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
