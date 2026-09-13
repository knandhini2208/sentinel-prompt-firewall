"""Read data/attack_patterns.csv, embed each pattern, insert into Exasol."""
import csv
import json
from pathlib import Path

from db import get_connection
from embeddings import embed

CSV_PATH = Path(__file__).parent.parent / "data" / "attack_patterns.csv"


def main():
    conn = get_connection()
    conn.execute("TRUNCATE TABLE SENTINEL.ATTACK_FINGERPRINTS")

    rows = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            vec = embed(row["pattern_text"])
            rows.append((row["category"], row["pattern_text"], json.dumps(vec.tolist())))

    for category, pattern_text, embedding_json in rows:
        conn.execute(
            "INSERT INTO SENTINEL.ATTACK_FINGERPRINTS (CATEGORY, PATTERN_TEXT, EMBEDDING) "
            "VALUES ({category}, {pattern_text}, {embedding})",
            {
                "category": category,
                "pattern_text": pattern_text,
                "embedding": embedding_json,
            },
        )
    print(f"Inserted {len(rows)} fingerprints.")


if __name__ == "__main__":
    main()
