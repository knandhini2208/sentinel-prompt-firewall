"""Run sql/schema.sql against the configured Exasol instance."""
from pathlib import Path
from db import get_connection

SCHEMA_PATH = Path(__file__).parent.parent / "sql" / "schema.sql"


def main():
    conn = get_connection()
    sql = SCHEMA_PATH.read_text()
    for statement in sql.split(";"):
        statement = statement.strip()
        if statement:
            conn.execute(statement)
    print("Schema created successfully.")


if __name__ == "__main__":
    main()
