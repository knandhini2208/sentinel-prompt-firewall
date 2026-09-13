"""Run sql/udf.sql to create the SCORE_SIMILARITY UDF inside Exasol."""
from pathlib import Path
from db import get_connection

UDF_PATH = Path(__file__).parent.parent / "sql" / "udf.sql"


def main():
    conn = get_connection()
    sql = UDF_PATH.read_text()

    conn.execute("OPEN SCHEMA SENTINEL")

    script_body = sql.split("OPEN SCHEMA SENTINEL;", 1)[1].strip()
    if script_body.endswith("/"):
        script_body = script_body[:-1].rstrip()

    conn.execute(script_body)
    print("UDF SENTINEL.SCORE_SIMILARITY created successfully.")


if __name__ == "__main__":
    main()