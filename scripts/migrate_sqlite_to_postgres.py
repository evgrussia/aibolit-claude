#!/usr/bin/env python3
"""Migrate data from SQLite to PostgreSQL.

Usage:
    python scripts/migrate_sqlite_to_postgres.py [--sqlite-path data/aibolit.db]

Requires DATABASE_URL env var to be set for PostgreSQL connection.
"""
import argparse
import os
import sqlite3
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text


def migrate(sqlite_path: str, pg_url: str) -> dict:
    """Migrate all data from SQLite to PostgreSQL."""
    if not os.path.isfile(sqlite_path):
        print(f"SQLite file not found: {sqlite_path}")
        return {"error": "SQLite file not found"}

    # Connect to SQLite
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row

    # Connect to PostgreSQL
    pg_engine = create_engine(pg_url)

    # Tables to migrate in dependency order
    tables = [
        "patients",
        "users",
        "allergies",
        "medications",
        "diagnoses",
        "lab_results",
        "vitals",
        "family_history",
        "surgical_history",
        "lifestyle",
        "genetic_markers",
        "consultations",
        "chat_messages",
        "chat_attachments",
        "documents",
        "audit_log",
    ]

    stats = {}

    for table in tables:
        try:
            rows = sqlite_conn.execute(f"SELECT * FROM {table}").fetchall()
            if not rows:
                stats[table] = 0
                continue

            columns = rows[0].keys()

            with pg_engine.begin() as pg_conn:
                for row in rows:
                    row_dict = dict(row)

                    # Handle BYTEA conversion for documents.content
                    if table == "documents" and "content" in row_dict and row_dict["content"] is not None:
                        row_dict["content"] = bytes(row_dict["content"])

                    # Build parameterized INSERT
                    cols = ", ".join(columns)
                    placeholders = ", ".join(f":{col}" for col in columns)

                    # Use ON CONFLICT DO NOTHING to skip duplicates
                    pg_conn.execute(
                        text(f"INSERT INTO {table} ({cols}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"),
                        row_dict,
                    )

                # Reset sequences for SERIAL columns
                if table != "patients" and table != "schema_version":
                    try:
                        pg_conn.execute(text(
                            f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
                            f"COALESCE((SELECT MAX(id) FROM {table}), 0) + 1, false)"
                        ))
                    except Exception:
                        pass  # Table might not have a serial column

            stats[table] = len(rows)
            print(f"  {table}: {len(rows)} rows migrated")

        except Exception as e:
            stats[table] = f"ERROR: {e}"
            print(f"  {table}: ERROR - {e}")

    sqlite_conn.close()
    pg_engine.dispose()

    return stats


def main():
    parser = argparse.ArgumentParser(description="Migrate SQLite data to PostgreSQL")
    parser.add_argument(
        "--sqlite-path",
        default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "aibolit.db"),
        help="Path to SQLite database file",
    )
    args = parser.parse_args()

    pg_url = os.getenv("DATABASE_URL")
    if not pg_url:
        print("ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)

    print(f"Migrating from: {args.sqlite_path}")
    print(f"Migrating to: {pg_url.split('@')[1] if '@' in pg_url else pg_url}")
    print()

    # First, initialize the PostgreSQL schema
    from src.utils.database import init_db
    print("Initializing PostgreSQL schema...")
    init_db()
    print("Schema created.")
    print()

    print("Migrating data...")
    stats = migrate(args.sqlite_path, pg_url)

    print()
    print("Migration complete:")
    total = 0
    for table, count in stats.items():
        if isinstance(count, int):
            total += count
    print(f"  Total rows migrated: {total}")


if __name__ == "__main__":
    main()
