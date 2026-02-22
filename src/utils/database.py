"""SQLite database backend for Aibolit patient records.

Replaces JSON file-based storage with a normalized relational schema.
Uses Python's built-in sqlite3 module — no external dependencies.
"""
import json
import os
import sqlite3
import sys
import threading
from datetime import date, datetime
from typing import Any

from ..models.patient import (
    Patient, VitalSigns, Allergy, Medication, LabResult,
    Diagnosis, Gender, BloodType,
)

# ── Database path ────────────────────────────────────────────
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data", "aibolit.db",
)

# ── Thread-local connection storage ──────────────────────────
_local = threading.local()

# ── Schema DDL ───────────────────────────────────────────────
SCHEMA_SQL = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS patients (
    id              TEXT PRIMARY KEY,
    first_name      TEXT NOT NULL,
    last_name       TEXT NOT NULL,
    date_of_birth   TEXT NOT NULL,
    gender          TEXT NOT NULL CHECK (gender IN ('male', 'female', 'other')),
    blood_type      TEXT,
    notes           TEXT NOT NULL DEFAULT '',
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS allergies (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id      TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    substance       TEXT NOT NULL,
    reaction        TEXT NOT NULL DEFAULT '',
    severity        TEXT NOT NULL DEFAULT 'moderate',
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_allergies_patient ON allergies(patient_id);

CREATE TABLE IF NOT EXISTS medications (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id          TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    name                TEXT NOT NULL,
    dosage              TEXT NOT NULL,
    frequency           TEXT NOT NULL,
    route               TEXT NOT NULL DEFAULT 'oral',
    start_date          TEXT,
    end_date            TEXT,
    prescribing_doctor  TEXT NOT NULL DEFAULT '',
    notes               TEXT NOT NULL DEFAULT '',
    created_at          TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_medications_patient ON medications(patient_id);

CREATE TABLE IF NOT EXISTS diagnoses (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id      TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    icd10_code      TEXT NOT NULL,
    name            TEXT NOT NULL,
    date_diagnosed  TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'active',
    notes           TEXT NOT NULL DEFAULT '',
    confidence      REAL NOT NULL DEFAULT 0.0,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_diagnoses_patient ON diagnoses(patient_id);
CREATE INDEX IF NOT EXISTS idx_diagnoses_status ON diagnoses(patient_id, status);
CREATE INDEX IF NOT EXISTS idx_diagnoses_icd10 ON diagnoses(icd10_code);

CREATE TABLE IF NOT EXISTS lab_results (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id      TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    test_name       TEXT NOT NULL,
    value           TEXT NOT NULL,
    unit            TEXT NOT NULL DEFAULT '',
    reference_range TEXT NOT NULL DEFAULT '',
    date            TEXT NOT NULL,
    is_abnormal     INTEGER NOT NULL DEFAULT 0,
    notes           TEXT NOT NULL DEFAULT '',
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_lab_results_patient ON lab_results(patient_id);
CREATE INDEX IF NOT EXISTS idx_lab_results_test ON lab_results(patient_id, test_name);
CREATE INDEX IF NOT EXISTS idx_lab_results_date ON lab_results(patient_id, date);

CREATE TABLE IF NOT EXISTS vitals (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id      TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    timestamp       TEXT NOT NULL,
    systolic_bp     INTEGER,
    diastolic_bp    INTEGER,
    heart_rate      INTEGER,
    temperature     REAL,
    spo2            REAL,
    respiratory_rate INTEGER,
    weight          REAL,
    height          REAL,
    blood_glucose   REAL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_vitals_patient ON vitals(patient_id);
CREATE INDEX IF NOT EXISTS idx_vitals_timestamp ON vitals(patient_id, timestamp);

CREATE TABLE IF NOT EXISTS family_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id      TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    description     TEXT NOT NULL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_family_history_patient ON family_history(patient_id);

CREATE TABLE IF NOT EXISTS surgical_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id      TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    description     TEXT NOT NULL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_surgical_history_patient ON surgical_history(patient_id);

CREATE TABLE IF NOT EXISTS lifestyle (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id      TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    key             TEXT NOT NULL,
    value           TEXT NOT NULL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_lifestyle_patient ON lifestyle(patient_id);

CREATE TABLE IF NOT EXISTS genetic_markers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id      TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    key             TEXT NOT NULL,
    value           TEXT NOT NULL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_genetic_markers_patient ON genetic_markers(patient_id);

CREATE TABLE IF NOT EXISTS consultations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id      TEXT REFERENCES patients(id) ON DELETE SET NULL,
    specialty       TEXT NOT NULL,
    complaints      TEXT NOT NULL,
    response        TEXT NOT NULL,
    date            TEXT NOT NULL DEFAULT (datetime('now')),
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_consultations_patient ON consultations(patient_id);
CREATE INDEX IF NOT EXISTS idx_consultations_specialty ON consultations(specialty);
CREATE INDEX IF NOT EXISTS idx_consultations_date ON consultations(date);

CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT UNIQUE NOT NULL,
    password_hash   TEXT NOT NULL,
    patient_id      TEXT REFERENCES patients(id),
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_patient ON users(patient_id);

CREATE TABLE IF NOT EXISTS documents (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id      TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    file_name       TEXT NOT NULL,
    file_type       TEXT NOT NULL DEFAULT '',
    file_size       INTEGER NOT NULL DEFAULT 0,
    content         BLOB NOT NULL,
    notes           TEXT NOT NULL DEFAULT '',
    uploaded_at     TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_documents_patient ON documents(patient_id);

CREATE TABLE IF NOT EXISTS schema_version (
    version     INTEGER PRIMARY KEY,
    applied_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


# ══════════════════════════════════════════════════════════════
# Connection management
# ══════════════════════════════════════════════════════════════

def _unicode_lower(value: str | None) -> str | None:
    """Python-based LOWER for SQLite — handles Cyrillic and other Unicode."""
    return value.lower() if value else value


def get_connection() -> sqlite3.Connection:
    """Get or create a thread-local database connection."""
    conn = getattr(_local, "conn", None)
    if conn is None:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA busy_timeout = 5000")
        # Register Unicode-aware LOWER function (SQLite's built-in only handles ASCII)
        conn.create_function("PY_LOWER", 1, _unicode_lower)
        _local.conn = conn
    return conn


def close_db() -> None:
    """Close the thread-local connection."""
    conn = getattr(_local, "conn", None)
    if conn is not None:
        conn.close()
        _local.conn = None


def init_db() -> None:
    """Create all tables if they don't exist. Auto-migrates JSON data on first run."""
    conn = get_connection()
    conn.executescript(SCHEMA_SQL)

    # Insert schema version if not present
    row = conn.execute("SELECT COUNT(*) FROM schema_version").fetchone()
    if row[0] == 0:
        conn.execute("INSERT INTO schema_version (version) VALUES (1)")
        conn.commit()

    # Auto-migrate from JSON if database is empty
    count = conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
    if count == 0:
        json_dir = os.path.join(os.path.dirname(DB_PATH), "patients")
        if os.path.isdir(json_dir) and any(f.endswith(".json") for f in os.listdir(json_dir)):
            result = migrate_from_json(json_dir)
            print(
                f"[Aibolit] Auto-migrated {result['migrated']} patients from JSON to SQLite",
                file=sys.stderr,
            )
            if result["errors"]:
                for err in result["errors"]:
                    print(f"[Aibolit] Migration error: {err}", file=sys.stderr)


# ══════════════════════════════════════════════════════════════
# Patient CRUD
# ══════════════════════════════════════════════════════════════

def save_patient(patient: Patient) -> str:
    """Insert or update a complete patient record atomically.
    Uses replace-all-children strategy within a transaction.
    Returns patient ID.
    """
    conn = get_connection()
    with conn:
        # Upsert patient row
        conn.execute(
            """INSERT INTO patients (id, first_name, last_name, date_of_birth, gender, blood_type, notes, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
               ON CONFLICT(id) DO UPDATE SET
                   first_name=excluded.first_name, last_name=excluded.last_name,
                   date_of_birth=excluded.date_of_birth, gender=excluded.gender,
                   blood_type=excluded.blood_type, notes=excluded.notes,
                   updated_at=datetime('now')""",
            (
                patient.id,
                patient.first_name,
                patient.last_name,
                patient.date_of_birth.isoformat(),
                patient.gender.value,
                patient.blood_type.value if patient.blood_type else None,
                patient.notes,
            ),
        )

        # Delete all child rows, then re-insert
        for table in (
            "allergies", "medications", "diagnoses", "lab_results",
            "vitals", "family_history", "surgical_history",
            "lifestyle", "genetic_markers",
        ):
            conn.execute(f"DELETE FROM {table} WHERE patient_id = ?", (patient.id,))

        # Allergies
        for a in patient.allergies:
            conn.execute(
                "INSERT INTO allergies (patient_id, substance, reaction, severity) VALUES (?, ?, ?, ?)",
                (patient.id, a.substance, a.reaction, a.severity),
            )

        # Medications
        for m in patient.medications:
            conn.execute(
                """INSERT INTO medications
                   (patient_id, name, dosage, frequency, route, start_date, end_date, prescribing_doctor, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    patient.id, m.name, m.dosage, m.frequency, m.route,
                    m.start_date.isoformat() if m.start_date else None,
                    m.end_date.isoformat() if m.end_date else None,
                    m.prescribing_doctor, m.notes,
                ),
            )

        # Diagnoses
        for d in patient.diagnoses:
            conn.execute(
                """INSERT INTO diagnoses
                   (patient_id, icd10_code, name, date_diagnosed, status, notes, confidence)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    patient.id, d.icd10_code, d.name,
                    d.date_diagnosed.isoformat(), d.status, d.notes, d.confidence,
                ),
            )

        # Lab results
        for lr in patient.lab_results:
            conn.execute(
                """INSERT INTO lab_results
                   (patient_id, test_name, value, unit, reference_range, date, is_abnormal, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    patient.id, lr.test_name, str(lr.value), lr.unit,
                    lr.reference_range, lr.date.isoformat(),
                    1 if lr.is_abnormal else 0, lr.notes,
                ),
            )

        # Vitals
        for v in patient.vitals_history:
            conn.execute(
                """INSERT INTO vitals
                   (patient_id, timestamp, systolic_bp, diastolic_bp, heart_rate,
                    temperature, spo2, respiratory_rate, weight, height, blood_glucose)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    patient.id, v.timestamp.isoformat(),
                    v.systolic_bp, v.diastolic_bp, v.heart_rate,
                    v.temperature, v.spo2, v.respiratory_rate,
                    v.weight, v.height, v.blood_glucose,
                ),
            )

        # Family history
        for desc in patient.family_history:
            conn.execute(
                "INSERT INTO family_history (patient_id, description) VALUES (?, ?)",
                (patient.id, desc),
            )

        # Surgical history
        for desc in patient.surgical_history:
            conn.execute(
                "INSERT INTO surgical_history (patient_id, description) VALUES (?, ?)",
                (patient.id, desc),
            )

        # Lifestyle
        for k, v in patient.lifestyle.items():
            conn.execute(
                "INSERT INTO lifestyle (patient_id, key, value) VALUES (?, ?, ?)",
                (patient.id, k, v),
            )

        # Genetic markers
        for k, v in patient.genetic_markers.items():
            conn.execute(
                "INSERT INTO genetic_markers (patient_id, key, value) VALUES (?, ?, ?)",
                (patient.id, k, json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v),
            )

    return patient.id


def load_patient(patient_id: str) -> Patient | None:
    """Load a complete Patient object with all related data."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
    if not row:
        return None

    pid = row["id"]

    # Allergies
    allergies = [
        Allergy(substance=r["substance"], reaction=r["reaction"], severity=r["severity"])
        for r in conn.execute("SELECT * FROM allergies WHERE patient_id = ?", (pid,))
    ]

    # Medications
    medications = [
        Medication(
            name=r["name"], dosage=r["dosage"], frequency=r["frequency"],
            route=r["route"],
            start_date=date.fromisoformat(r["start_date"]) if r["start_date"] else None,
            end_date=date.fromisoformat(r["end_date"]) if r["end_date"] else None,
            prescribing_doctor=r["prescribing_doctor"], notes=r["notes"],
        )
        for r in conn.execute("SELECT * FROM medications WHERE patient_id = ?", (pid,))
    ]

    # Diagnoses
    diagnoses = [
        Diagnosis(
            icd10_code=r["icd10_code"], name=r["name"],
            date_diagnosed=date.fromisoformat(r["date_diagnosed"]),
            status=r["status"], notes=r["notes"], confidence=r["confidence"],
        )
        for r in conn.execute("SELECT * FROM diagnoses WHERE patient_id = ?", (pid,))
    ]

    # Lab results
    lab_results = [
        LabResult(
            test_name=r["test_name"],
            value=_parse_lab_value(r["value"]),
            unit=r["unit"], reference_range=r["reference_range"],
            date=date.fromisoformat(r["date"]),
            is_abnormal=bool(r["is_abnormal"]), notes=r["notes"],
        )
        for r in conn.execute(
            "SELECT * FROM lab_results WHERE patient_id = ? ORDER BY date", (pid,)
        )
    ]

    # Vitals
    vitals_history = [
        VitalSigns(
            timestamp=datetime.fromisoformat(r["timestamp"]),
            systolic_bp=r["systolic_bp"], diastolic_bp=r["diastolic_bp"],
            heart_rate=r["heart_rate"], temperature=r["temperature"],
            spo2=r["spo2"], respiratory_rate=r["respiratory_rate"],
            weight=r["weight"], height=r["height"],
            blood_glucose=r["blood_glucose"],
        )
        for r in conn.execute(
            "SELECT * FROM vitals WHERE patient_id = ? ORDER BY timestamp", (pid,)
        )
    ]

    # Simple lists
    family_history = [
        r["description"]
        for r in conn.execute("SELECT description FROM family_history WHERE patient_id = ?", (pid,))
    ]
    surgical_history = [
        r["description"]
        for r in conn.execute("SELECT description FROM surgical_history WHERE patient_id = ?", (pid,))
    ]

    # Key-value dicts
    lifestyle = {
        r["key"]: r["value"]
        for r in conn.execute("SELECT key, value FROM lifestyle WHERE patient_id = ?", (pid,))
    }
    genetic_markers: dict[str, Any] = {}
    for r in conn.execute("SELECT key, value FROM genetic_markers WHERE patient_id = ?", (pid,)):
        try:
            genetic_markers[r["key"]] = json.loads(r["value"])
        except (json.JSONDecodeError, TypeError):
            genetic_markers[r["key"]] = r["value"]

    return Patient(
        id=pid,
        first_name=row["first_name"],
        last_name=row["last_name"],
        date_of_birth=date.fromisoformat(row["date_of_birth"]),
        gender=Gender(row["gender"]),
        blood_type=BloodType(row["blood_type"]) if row["blood_type"] else None,
        allergies=allergies,
        medications=medications,
        diagnoses=diagnoses,
        lab_results=lab_results,
        vitals_history=vitals_history,
        family_history=family_history,
        surgical_history=surgical_history,
        lifestyle=lifestyle,
        genetic_markers=genetic_markers,
        notes=row["notes"],
    )


def list_patients() -> list[dict[str, str]]:
    """Return summary list of all patients."""
    conn = get_connection()
    return [
        {
            "id": r["id"],
            "name": f"{r['last_name']} {r['first_name']}",
            "dob": r["date_of_birth"],
            "gender": r["gender"],
        }
        for r in conn.execute(
            "SELECT id, first_name, last_name, date_of_birth, gender FROM patients ORDER BY last_name"
        )
    ]


def delete_patient(patient_id: str) -> bool:
    """Delete a patient and all related data (cascade). Returns True if deleted."""
    conn = get_connection()
    with conn:
        cursor = conn.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
    return cursor.rowcount > 0


# ══════════════════════════════════════════════════════════════
# Granular insert operations
# ══════════════════════════════════════════════════════════════

def _check_patient_exists(conn: sqlite3.Connection, patient_id: str) -> None:
    """Raise ValueError if patient does not exist."""
    row = conn.execute("SELECT 1 FROM patients WHERE id = ?", (patient_id,)).fetchone()
    if not row:
        raise ValueError(f"Пациент {patient_id} не найден")


def add_vitals(patient_id: str, vitals: VitalSigns) -> int:
    """Insert a single vitals record. Returns the new row ID."""
    conn = get_connection()
    with conn:
        _check_patient_exists(conn, patient_id)
        cursor = conn.execute(
            """INSERT INTO vitals
               (patient_id, timestamp, systolic_bp, diastolic_bp, heart_rate,
                temperature, spo2, respiratory_rate, weight, height, blood_glucose)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                patient_id, vitals.timestamp.isoformat(),
                vitals.systolic_bp, vitals.diastolic_bp, vitals.heart_rate,
                vitals.temperature, vitals.spo2, vitals.respiratory_rate,
                vitals.weight, vitals.height, vitals.blood_glucose,
            ),
        )
        conn.execute(
            "UPDATE patients SET updated_at = datetime('now') WHERE id = ?",
            (patient_id,),
        )
    return cursor.lastrowid


def add_lab_result(patient_id: str, lab_result: LabResult) -> int:
    """Insert a single lab result. Returns the new row ID."""
    conn = get_connection()
    with conn:
        _check_patient_exists(conn, patient_id)
        cursor = conn.execute(
            """INSERT INTO lab_results
               (patient_id, test_name, value, unit, reference_range, date, is_abnormal, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                patient_id, lab_result.test_name, str(lab_result.value),
                lab_result.unit, lab_result.reference_range,
                lab_result.date.isoformat(),
                1 if lab_result.is_abnormal else 0,
                lab_result.notes,
            ),
        )
        conn.execute(
            "UPDATE patients SET updated_at = datetime('now') WHERE id = ?",
            (patient_id,),
        )
    return cursor.lastrowid


def add_diagnosis(patient_id: str, diagnosis: Diagnosis) -> int:
    """Insert a single diagnosis. Returns the new row ID."""
    conn = get_connection()
    with conn:
        _check_patient_exists(conn, patient_id)
        cursor = conn.execute(
            """INSERT INTO diagnoses
               (patient_id, icd10_code, name, date_diagnosed, status, notes, confidence)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                patient_id, diagnosis.icd10_code, diagnosis.name,
                diagnosis.date_diagnosed.isoformat(), diagnosis.status,
                diagnosis.notes, diagnosis.confidence,
            ),
        )
        conn.execute(
            "UPDATE patients SET updated_at = datetime('now') WHERE id = ?",
            (patient_id,),
        )
    return cursor.lastrowid


def add_medication(patient_id: str, medication: Medication) -> int:
    """Insert a single medication. Returns the new row ID."""
    conn = get_connection()
    with conn:
        _check_patient_exists(conn, patient_id)
        cursor = conn.execute(
            """INSERT INTO medications
               (patient_id, name, dosage, frequency, route, start_date, end_date, prescribing_doctor, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                patient_id, medication.name, medication.dosage,
                medication.frequency, medication.route,
                medication.start_date.isoformat() if medication.start_date else None,
                medication.end_date.isoformat() if medication.end_date else None,
                medication.prescribing_doctor, medication.notes,
            ),
        )
        conn.execute(
            "UPDATE patients SET updated_at = datetime('now') WHERE id = ?",
            (patient_id,),
        )
    return cursor.lastrowid


def add_allergy(patient_id: str, allergy: Allergy) -> int:
    """Insert a single allergy. Returns the new row ID."""
    conn = get_connection()
    with conn:
        _check_patient_exists(conn, patient_id)
        cursor = conn.execute(
            "INSERT INTO allergies (patient_id, substance, reaction, severity) VALUES (?, ?, ?, ?)",
            (patient_id, allergy.substance, allergy.reaction, allergy.severity),
        )
        conn.execute(
            "UPDATE patients SET updated_at = datetime('now') WHERE id = ?",
            (patient_id,),
        )
    return cursor.lastrowid


# ══════════════════════════════════════════════════════════════
# Consultation history
# ══════════════════════════════════════════════════════════════

def save_consultation(
    specialty: str,
    complaints: str,
    response: dict,
    patient_id: str | None = None,
) -> int:
    """Store a consultation record. Returns consultation row ID."""
    conn = get_connection()
    with conn:
        cursor = conn.execute(
            """INSERT INTO consultations (patient_id, specialty, complaints, response)
               VALUES (?, ?, ?, ?)""",
            (patient_id, specialty, complaints, json.dumps(response, ensure_ascii=False)),
        )
    return cursor.lastrowid


def get_consultation_history(
    patient_id: str | None = None,
    specialty: str | None = None,
    limit: int = 50,
) -> list[dict]:
    """Retrieve consultation history filtered by patient and/or specialty."""
    conn = get_connection()
    clauses = []
    params: list[Any] = []

    if patient_id:
        clauses.append("c.patient_id = ?")
        params.append(patient_id)
    if specialty:
        clauses.append("c.specialty = ?")
        params.append(specialty)

    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    params.append(limit)

    rows = conn.execute(
        f"""SELECT c.id, c.patient_id, c.specialty, c.complaints, c.response, c.date,
                   p.first_name, p.last_name
            FROM consultations c
            LEFT JOIN patients p ON c.patient_id = p.id
            {where}
            ORDER BY c.date DESC
            LIMIT ?""",
        params,
    ).fetchall()

    results = []
    for r in rows:
        entry = {
            "id": r["id"],
            "patient_id": r["patient_id"],
            "patient_name": f"{r['last_name']} {r['first_name']}" if r["first_name"] else None,
            "specialty": r["specialty"],
            "complaints": r["complaints"],
            "date": r["date"],
        }
        try:
            entry["response"] = json.loads(r["response"])
        except (json.JSONDecodeError, TypeError):
            entry["response"] = r["response"]
        results.append(entry)

    return results


# ══════════════════════════════════════════════════════════════
# Query / analytics operations
# ══════════════════════════════════════════════════════════════

def get_lab_trends(patient_id: str, test_name: str, limit: int = 20) -> list[dict]:
    """Get historical lab results for a specific test, ordered by date ascending."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT test_name, value, unit, reference_range, date, is_abnormal, notes
           FROM lab_results
           WHERE patient_id = ? AND PY_LOWER(test_name) LIKE PY_LOWER(?)
           ORDER BY date ASC
           LIMIT ?""",
        (patient_id, f"%{test_name}%", limit),
    ).fetchall()

    return [
        {
            "test_name": r["test_name"],
            "value": _parse_lab_value(r["value"]),
            "unit": r["unit"],
            "reference_range": r["reference_range"],
            "date": r["date"],
            "is_abnormal": bool(r["is_abnormal"]),
            "notes": r["notes"],
        }
        for r in rows
    ]


def get_vitals_trends(patient_id: str, limit: int = 20) -> list[dict]:
    """Get historical vitals records ordered by timestamp descending."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT timestamp, systolic_bp, diastolic_bp, heart_rate, temperature,
                  spo2, respiratory_rate, weight, height, blood_glucose
           FROM vitals
           WHERE patient_id = ?
           ORDER BY timestamp DESC
           LIMIT ?""",
        (patient_id, limit),
    ).fetchall()

    return [dict(r) for r in rows]


def search_patients(query: str) -> list[dict[str, str]]:
    """Search patients by name (partial match)."""
    conn = get_connection()
    pattern = f"%{query}%"
    rows = conn.execute(
        """SELECT id, first_name, last_name, date_of_birth, gender
           FROM patients
           WHERE PY_LOWER(first_name) LIKE PY_LOWER(?) OR PY_LOWER(last_name) LIKE PY_LOWER(?)
           ORDER BY last_name""",
        (pattern, pattern),
    ).fetchall()

    return [
        {
            "id": r["id"],
            "name": f"{r['last_name']} {r['first_name']}",
            "dob": r["date_of_birth"],
            "gender": r["gender"],
        }
        for r in rows
    ]


def get_patients_by_diagnosis(icd10_prefix: str) -> list[dict]:
    """Find all patients with a diagnosis matching an ICD-10 prefix."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT DISTINCT p.id AS patient_id,
                  p.last_name || ' ' || p.first_name AS patient_name,
                  d.name AS diagnosis, d.icd10_code, d.status
           FROM diagnoses d
           JOIN patients p ON d.patient_id = p.id
           WHERE d.icd10_code LIKE ?
           ORDER BY p.last_name""",
        (f"{icd10_prefix}%",),
    ).fetchall()

    return [dict(r) for r in rows]


# ══════════════════════════════════════════════════════════════
# Migration from JSON
# ══════════════════════════════════════════════════════════════

def migrate_from_json(json_dir: str) -> dict:
    """Read all JSON patient files and insert them into SQLite.
    Skips patients that already exist. Returns {"migrated": N, "errors": [...]}.
    """
    from .patient_db import _dict_to_patient

    migrated = 0
    errors = []

    for fname in os.listdir(json_dir):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(json_dir, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            patient = _dict_to_patient(data)
            if load_patient(patient.id) is None:
                save_patient(patient)
                migrated += 1
        except Exception as e:
            errors.append(f"{fname}: {e}")

    return {"migrated": migrated, "errors": errors}


# ══════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════

def _parse_lab_value(raw: str) -> float | str:
    """Try to parse a lab value as float; return string if it fails."""
    try:
        return float(raw)
    except (ValueError, TypeError):
        return raw


# ══════════════════════════════════════════════════════════════
# User management
# ══════════════════════════════════════════════════════════════

def create_user(username: str, password_hash: str, patient_id: str | None = None) -> int:
    """Create a new user. Returns user ID."""
    conn = get_connection()
    with conn:
        cursor = conn.execute(
            "INSERT INTO users (username, password_hash, patient_id) VALUES (?, ?, ?)",
            (username, password_hash, patient_id),
        )
    return cursor.lastrowid


def get_user_by_username(username: str) -> dict | None:
    """Fetch user by username. Returns dict or None."""
    conn = get_connection()
    row = conn.execute(
        "SELECT id, username, password_hash, patient_id, created_at FROM users WHERE username = ?",
        (username,),
    ).fetchone()
    return dict(row) if row else None


def get_user_by_id(user_id: int) -> dict | None:
    """Fetch user by ID. Returns dict or None."""
    conn = get_connection()
    row = conn.execute(
        "SELECT id, username, password_hash, patient_id, created_at FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    return dict(row) if row else None


def link_user_to_patient(user_id: int, patient_id: str) -> None:
    """Link user account to a patient record."""
    conn = get_connection()
    with conn:
        conn.execute(
            "UPDATE users SET patient_id = ? WHERE id = ?",
            (patient_id, user_id),
        )


# ══════════════════════════════════════════════════════════════
# Document storage
# ══════════════════════════════════════════════════════════════

def save_document(
    patient_id: str,
    file_name: str,
    file_type: str,
    file_size: int,
    content: bytes,
    notes: str = "",
) -> int:
    """Store an uploaded document. Returns document row ID."""
    conn = get_connection()
    with conn:
        _check_patient_exists(conn, patient_id)
        cursor = conn.execute(
            """INSERT INTO documents (patient_id, file_name, file_type, file_size, content, notes)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (patient_id, file_name, file_type, file_size, content, notes),
        )
    return cursor.lastrowid


def list_documents(patient_id: str) -> list[dict]:
    """List documents for a patient (without BLOB content)."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT id, file_name, file_type, file_size, notes, uploaded_at
           FROM documents WHERE patient_id = ? ORDER BY uploaded_at DESC""",
        (patient_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def get_document(doc_id: int) -> dict | None:
    """Fetch a single document with its content."""
    conn = get_connection()
    row = conn.execute(
        "SELECT id, patient_id, file_name, file_type, file_size, content, notes, uploaded_at FROM documents WHERE id = ?",
        (doc_id,),
    ).fetchone()
    return dict(row) if row else None


def delete_document(doc_id: int) -> bool:
    """Delete a document by ID. Returns True if deleted."""
    conn = get_connection()
    with conn:
        cursor = conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    return cursor.rowcount > 0
