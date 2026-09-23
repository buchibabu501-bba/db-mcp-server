# cassandra-mcp-server

Read-only MCP server for a Cassandra cluster.

## Tools

- `list_keyspaces()` — non-system keyspaces
- `list_tables(keyspace)` — tables in a keyspace
- `describe_table(keyspace, table)` — column names, types, and kind (partition key / clustering / regular / static)
- `execute_cql(query)` — run a `SELECT` statement (only `SELECT` is permitted)

## Setup

```bash
cd servers/cassandra
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

| Env var | Default | Notes |
|---|---|---|
| `CASSANDRA_CONTACT_POINTS` | `127.0.0.1` | comma-separated hosts |
| `CASSANDRA_PORT` | `9042` | |
| `CASSANDRA_LOCAL_DATACENTER` | `datacenter1` | required by the driver's default load-balancing policy |
| `CASSANDRA_USERNAME` | — | optional |
| `CASSANDRA_PASSWORD` | — | optional |
| `CASSANDRA_KEYSPACE` | — | optional default keyspace for the session |

## Add to an MCP client

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
    }
  }
}
```
