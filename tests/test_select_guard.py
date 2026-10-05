import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _load(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SERVERS = {
    "cassandra": _load("cassandra_server", "servers/cassandra/server.py"),
    "yugabytedb": _load("yugabytedb_server", "servers/yugabytedb/server.py"),
}


@pytest.fixture(params=SERVERS.keys())
def validate(request):
    return SERVERS[request.param]._validate_select


def test_plain_select_is_allowed(validate):
    assert validate("SELECT * FROM users") == "SELECT * FROM users"


def test_case_and_leading_whitespace_are_allowed(validate):
    assert validate("  \n select 1") == "select 1"


def test_single_trailing_semicolon_is_stripped(validate):
    assert validate("SELECT 1;") == "SELECT 1"


@pytest.mark.parametrize(
    "query",
    [
        "INSERT INTO users VALUES (1)",
        "UPDATE users SET name = 'x'",
        "DELETE FROM users",
        "DROP TABLE users",
        "TRUNCATE users",
        "SET default_transaction_read_only = off",
        "",
        "   ",
    ],
)
def test_non_select_is_rejected(validate, query):
    with pytest.raises(ValueError, match="Only SELECT"):
        validate(query)


@pytest.mark.parametrize(
    "query",
    [
        "SELECT 1; DROP TABLE users",
        "SELECT 1; SET default_transaction_read_only = off; DROP TABLE users",
        "SELECT 1;; SELECT 2",
    ],
)
def test_multiple_statements_are_rejected(validate, query):
    with pytest.raises(ValueError, match="Multiple statements"):
        validate(query)


def test_select_prefix_lookalike_is_rejected(validate):
    with pytest.raises(ValueError, match="Only SELECT"):
        validate("SELECTED_FUNCTION()")
