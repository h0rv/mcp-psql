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

    def get_table_names(self) -> list[str]:
        with self.cursor() as cur:
            cur.execute(
                """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            """
            )
            return [row[0] for row in cur]

    @property
    def table_names(self) -> list[str]:
        if not hasattr(self, "_table_names"):
            with self.cursor() as cur:
                cur.execute(
                    """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                    """
                )
                self._table_names = [row[0] for row in cur]
        return self._table_names

    def get_table_schema(self, table_name: str) -> str:
        with self.cursor() as cur:
            cur.execute(
                f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'"
            )
            return str(cur.fetchall())


conn = DatabaseConnection()


class TableSchemaResource(Resource):
    table_name: str

    async def read(self) -> str:
        return conn.get_table_schema(self.table_name)


def add_schema_resources() -> None:
    for table_name in conn.table_names:
        mcp.add_resource(
            TableSchemaResource(
                uri=f"resource://{table_name}/{SCHEMA_PATH}",
                name=f"'{table_name}' database schema",
                table_name=table_name,
            )
        )


add_schema_resources()


@mcp.tool(description="Run a read-only SQL query")
async def query(query: str) -> str:
    with conn.cursor() as cur:
        cur.execute("BEGIN TRANSACTION READ ONLY")  # TODO: is this right?
        cur.execute(query)
        result = cur.fetchall()
        return str(result)


@mcp.tool(description="List all tables in the database")
async def list_tables() -> str:
    return str(conn.table_names)


@mcp.tool(description="Get the schema of a table in the database")
async def get_table_schema(table_name: str) -> str:
    return conn.get_table_schema(table_name)


@mcp.tool(description="Get the schema of tables in the database")
async def get_table_schemas(table_names: list[str]) -> str:
    return [conn.get_table_schema(table_name) for table_name in table_names]


def main():
    import argparse

    args = argparse.ArgumentParser()
    args.add_argument("--transport", type=str, default="stdio")
    args.add_argument("--port", type=int, default=8000)
    args = args.parse_args()

    mcp.run(
        transport=args.transport,
    )


if __name__ == "__main__":
    main()
