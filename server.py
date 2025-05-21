import os
import atexit

import psycopg
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.resources import Resource


mcp = FastMCP(
    name="psql",
    version="0.1.0",
)


SCHEMA_PATH = os.environ.get("DATABASE_SCHEMA_PATH") or "schema"


class DatabaseConnection:
    def __init__(self):
        db_uri = os.environ.get("DATABASE_URI") or os.environ.get("DB_URI")
        if not db_uri:
            raise ValueError(
                "Please provide a database uri with DATABASE_URI or DB_URI environment variable"
            )

        if not (db_uri.startswith("postgres://") or db_uri.startswith("postgresql://")):
            raise ValueError(
                "Database URI must start with postgres:// or postgresql://"
            )

        self.conn = psycopg.connect(db_uri)
        atexit.register(lambda: self.conn.close())

    def __getattr__(self, name: str):
        # Forward all attribute access to the underlying connection
        return getattr(self.conn, name)


conn = DatabaseConnection()


class TableSchemaResource(Resource):
    table_name: str

    async def read(self) -> str:
        with conn.cursor() as cur:
            cur.execute(
                f"""\
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = '{self.table_name}'
    """
            )
            return str(cur.fetchall())


def add_schema_resources() -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        """
        )

        for row in cur:
            table_name = row[0]
            mcp.add_resource(
                TableSchemaResource(
                    uri=f"resource://{table_name}/{SCHEMA_PATH}",
                    name=f"'{table_name}' database schema",
                    table_name=table_name,
                )
            )


add_schema_resources()


@mcp.tool(
    name="query",
    description="Run a read-only SQL query",
)
async def query(query: str) -> str:
    with conn.cursor() as cur:
        cur.execute("BEGIN TRANSACTION READ ONLY")  # TODO: is this right?
        cur.execute(query)
        result = cur.fetchall()
        return str(result)
