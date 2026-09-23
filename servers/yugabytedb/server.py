"""MCP server exposing read-only access to a YugabyteDB (YSQL) database.

YSQL is PostgreSQL wire-compatible, so this talks to it with a standard
Postgres driver on YugabyteDB's default YSQL port (5433).

Configuration (environment variables):
  YUGABYTE_HOST      default "127.0.0.1"
  YUGABYTE_PORT      default 5433
  YUGABYTE_DATABASE  default "yugabyte"
  YUGABYTE_USER      default "yugabyte"
  YUGABYTE_PASSWORD  default ""
"""

import os
import re
from typing import Optional

import psycopg2
import psycopg2.extensions
import psycopg2.extras
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("yugabytedb")

_SELECT_RE = re.compile(r"^\s*select\b", re.IGNORECASE)
_conn: Optional[psycopg2.extensions.connection] = None


def _get_conn() -> psycopg2.extensions.connection:
    global _conn
    if _conn is not None and _conn.closed == 0:
        return _conn

    _conn = psycopg2.connect(
        host=os.environ.get("YUGABYTE_HOST", "127.0.0.1"),
        port=int(os.environ.get("YUGABYTE_PORT", "5433")),
        dbname=os.environ.get("YUGABYTE_DATABASE", "yugabyte"),
        user=os.environ.get("YUGABYTE_USER", "yugabyte"),
        password=os.environ.get("YUGABYTE_PASSWORD", ""),
    )
    _conn.set_session(readonly=True, autocommit=True)
    return _conn


@mcp.tool()
def list_schemas() -> list[str]:
    """List all non-system schemas in the database."""
    with _get_conn().cursor() as cur:
        cur.execute(
            "SELECT schema_name FROM information_schema.schemata "
            "WHERE schema_name NOT IN ('pg_catalog', 'information_schema') "
            "AND schema_name NOT LIKE 'pg_%' ORDER BY schema_name"
        )
        return [r[0] for r in cur.fetchall()]


@mcp.tool()
def list_tables(schema: str = "public") -> list[str]:
    """List all tables in a given schema (default: public)."""
    with _get_conn().cursor() as cur:
        cur.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = %s ORDER BY table_name",
            (schema,),
        )
        return [r[0] for r in cur.fetchall()]


@mcp.tool()
def describe_table(table: str, schema: str = "public") -> list[dict]:
    """Describe a table's columns: name, data type, nullability, and default."""
    with _get_conn().cursor() as cur:
        cur.execute(
            "SELECT column_name, data_type, is_nullable, column_default "
            "FROM information_schema.columns "
            "WHERE table_schema = %s AND table_name = %s "
            "ORDER BY ordinal_position",
            (schema, table),
        )
        return [
            {"column": r[0], "type": r[1], "nullable": r[2] == "YES", "default": r[3]}
            for r in cur.fetchall()
        ]


@mcp.tool()
def execute_sql(query: str) -> list[dict]:
    """Run a read-only SQL SELECT statement and return the matching rows.

    The connection is read-only, and only SELECT statements are permitted.
    """
    if not _SELECT_RE.match(query):
        raise ValueError("Only SELECT statements are allowed through execute_sql.")
    with _get_conn().cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(query)
        return [dict(row) for row in cur.fetchall()]


if __name__ == "__main__":
    mcp.run(transport="stdio")
