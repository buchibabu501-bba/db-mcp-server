"""MCP server exposing read-only access to a Cassandra cluster.

Configuration (environment variables):
  CASSANDRA_CONTACT_POINTS    comma-separated hosts, default "127.0.0.1"
  CASSANDRA_PORT              default 9042
  CASSANDRA_LOCAL_DATACENTER  default "datacenter1"
  CASSANDRA_USERNAME          optional
  CASSANDRA_PASSWORD          optional
  CASSANDRA_KEYSPACE          optional default keyspace for the session
"""

import os
import re
from typing import Optional

from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster, Session
from cassandra.policies import DCAwareRoundRobinPolicy
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("cassandra")

_SELECT_RE = re.compile(r"^\s*select\b", re.IGNORECASE)
_session: Optional[Session] = None


def _get_session() -> Session:
    global _session
    if _session is not None:
        return _session

    contact_points = [
        cp.strip()
        for cp in os.environ.get("CASSANDRA_CONTACT_POINTS", "127.0.0.1").split(",")
    ]
    port = int(os.environ.get("CASSANDRA_PORT", "9042"))
    local_dc = os.environ.get("CASSANDRA_LOCAL_DATACENTER", "datacenter1")
    username = os.environ.get("CASSANDRA_USERNAME")
    password = os.environ.get("CASSANDRA_PASSWORD")
    keyspace = os.environ.get("CASSANDRA_KEYSPACE") or None

    auth_provider = (
        PlainTextAuthProvider(username=username, password=password)
        if username and password
        else None
    )

    cluster = Cluster(
        contact_points=contact_points,
        port=port,
        auth_provider=auth_provider,
        load_balancing_policy=DCAwareRoundRobinPolicy(local_dc=local_dc),
    )
    _session = cluster.connect(keyspace)
    return _session


@mcp.tool()
def list_keyspaces() -> list[str]:
    """List all non-system keyspaces in the Cassandra cluster."""
    rows = _get_session().execute("SELECT keyspace_name FROM system_schema.keyspaces")
    return sorted(r.keyspace_name for r in rows if not r.keyspace_name.startswith("system"))


@mcp.tool()
def list_tables(keyspace: str) -> list[str]:
    """List all tables in a given keyspace."""
    rows = _get_session().execute(
        "SELECT table_name FROM system_schema.tables WHERE keyspace_name = %s",
        (keyspace,),
    )
    return sorted(r.table_name for r in rows)


@mcp.tool()
def describe_table(keyspace: str, table: str) -> list[dict]:
    """Describe a table's columns: name, CQL type, and kind (partition_key, clustering, regular, static)."""
    rows = _get_session().execute(
        "SELECT column_name, type, kind, position FROM system_schema.columns "
        "WHERE keyspace_name = %s AND table_name = %s",
        (keyspace, table),
    )
    return [
        {"column": r.column_name, "type": r.type, "kind": r.kind, "position": r.position}
        for r in rows
    ]


@mcp.tool()
def execute_cql(query: str) -> list[dict]:
    """Run a read-only CQL SELECT statement and return the matching rows.

    Only SELECT statements are permitted; anything else is rejected.
    """
    if not _SELECT_RE.match(query):
        raise ValueError("Only SELECT statements are allowed through execute_cql.")
    rows = _get_session().execute(query)
    return [dict(row._asdict()) for row in rows]


if __name__ == "__main__":
    mcp.run(transport="stdio")
