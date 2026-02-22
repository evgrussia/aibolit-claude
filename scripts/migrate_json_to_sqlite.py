#!/usr/bin/env python3
"""Migrate existing JSON patient files to SQLite database.

Usage:
    python -m scripts.migrate_json_to_sqlite

This script reads all JSON files from data/patients/ and inserts them
into the SQLite database at data/aibolit.db. Patients that already
exist in the database are skipped.

Note: The MCP server also performs auto-migration on first startup,
so this script is optional — useful for manual migration with verbose output.
"""
import os
import sys

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.utils.database import init_db, migrate_from_json, DB_PATH


def main():
    json_dir = os.path.join(PROJECT_ROOT, "data", "patients")

    if not os.path.isdir(json_dir):
        print(f"No JSON patient data directory found at: {json_dir}")
        print("Nothing to migrate.")
        return

    json_files = [f for f in os.listdir(json_dir) if f.endswith(".json")]
    if not json_files:
        print(f"No .json files found in {json_dir}")
        return

    print(f"Found {len(json_files)} JSON patient file(s) in {json_dir}")
    print(f"Database: {DB_PATH}")
    print()

    # Initialize database schema
    init_db()
    print("Database schema initialized.")

    # Run migration
    result = migrate_from_json(json_dir)

    print(f"\nMigration complete:")
    print(f"  Migrated: {result['migrated']} patient(s)")
    if result["errors"]:
        print(f"  Errors:   {len(result['errors'])}")
        for err in result["errors"]:
            print(f"    - {err}")
    else:
        print("  Errors:   0")

    if result["migrated"] > 0:
        print(f"\nJSON files are preserved in {json_dir} as backup.")
        print("You may rename the directory to data/patients_archived/ if desired.")


if __name__ == "__main__":
    main()
