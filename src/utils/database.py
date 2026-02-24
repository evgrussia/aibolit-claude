"""PostgreSQL database backend for Aibolit patient records.

Uses SQLAlchemy Core with psycopg2 connection pool.
All function signatures are preserved for backward compatibility.
"""
import json
import logging
import os
import sys
from datetime import date, datetime
from typing import Any

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.pool import QueuePool

from ..models.patient import (
    Patient, VitalSigns, Allergy, Medication, LabResult,
    Diagnosis, Gender, BloodType,
)
from .encryption import encrypt_field, decrypt_field

logger = logging.getLogger("aibolit.db")

# ── Database URL ─────────────────────────────────────────────
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://aibolit:aibolit@localhost:5432/aibolit",
)

# ── SQLAlchemy engine ────────────────────────────────────────
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
    pool_pre_ping=True,
    echo=False,
)

def get_connection():
    """Get a database connection from the pool.

    Returns a SQLAlchemy Connection object.
    Usage: with get_connection() as conn: ...
    """
    return engine.connect()


def close_db() -> None:
    """Dispose the engine connection pool."""
    engine.dispose()


# ══════════════════════════════════════════════════════════════
# Schema DDL (PostgreSQL)
# ══════════════════════════════════════════════════════════════

_TABLES_SQL = [
    """
    CREATE TABLE IF NOT EXISTS patients (
        id              TEXT PRIMARY KEY,
        first_name      TEXT NOT NULL,
        last_name       TEXT NOT NULL,
        date_of_birth   TEXT NOT NULL,
        gender          TEXT NOT NULL CHECK (gender IN ('male', 'female', 'other')),
        blood_type      TEXT,
        notes           TEXT NOT NULL DEFAULT '',
        created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
        updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS allergies (
        id              SERIAL PRIMARY KEY,
        patient_id      TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
        substance       TEXT NOT NULL,
        reaction        TEXT NOT NULL DEFAULT '',
        severity        TEXT NOT NULL DEFAULT 'moderate',
        created_at      TIMESTAMP NOT NULL DEFAULT NOW()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_allergies_patient ON allergies(patient_id)",
    """
    CREATE TABLE IF NOT EXISTS medications (
        id                  SERIAL PRIMARY KEY,
        patient_id          TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
        name                TEXT NOT NULL,
        dosage              TEXT NOT NULL,
        frequency           TEXT NOT NULL,
        route               TEXT NOT NULL DEFAULT 'oral',
        start_date          TEXT,
        end_date            TEXT,
        prescribing_doctor  TEXT NOT NULL DEFAULT '',
        notes               TEXT NOT NULL DEFAULT '',
        created_at          TIMESTAMP NOT NULL DEFAULT NOW()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_medications_patient ON medications(patient_id)",
    """
    CREATE TABLE IF NOT EXISTS diagnoses (
        id              SERIAL PRIMARY KEY,
        patient_id      TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
        icd10_code      TEXT NOT NULL,
        name            TEXT NOT NULL,
        date_diagnosed  TEXT NOT NULL,
        status          TEXT NOT NULL DEFAULT 'active',
        notes           TEXT NOT NULL DEFAULT '',
        confidence      REAL NOT NULL DEFAULT 0.0,
        created_at      TIMESTAMP NOT NULL DEFAULT NOW()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_diagnoses_patient ON diagnoses(patient_id)",
    "CREATE INDEX IF NOT EXISTS idx_diagnoses_status ON diagnoses(patient_id, status)",
    "CREATE INDEX IF NOT EXISTS idx_diagnoses_icd10 ON diagnoses(icd10_code)",
    """
    CREATE TABLE IF NOT EXISTS lab_results (
        id              SERIAL PRIMARY KEY,
        patient_id      TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
        test_name       TEXT NOT NULL,
        value           TEXT NOT NULL,
        unit            TEXT NOT NULL DEFAULT '',
        reference_range TEXT NOT NULL DEFAULT '',
        date            TEXT NOT NULL,
        is_abnormal     SMALLINT NOT NULL DEFAULT 0,
        notes           TEXT NOT NULL DEFAULT '',
        created_at      TIMESTAMP NOT NULL DEFAULT NOW()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_lab_results_patient ON lab_results(patient_id)",
    "CREATE INDEX IF NOT EXISTS idx_lab_results_test ON lab_results(patient_id, test_name)",
    "CREATE INDEX IF NOT EXISTS idx_lab_results_date ON lab_results(patient_id, date)",
    """
    CREATE TABLE IF NOT EXISTS vitals (
        id              SERIAL PRIMARY KEY,
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
        created_at      TIMESTAMP NOT NULL DEFAULT NOW()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_vitals_patient ON vitals(patient_id)",
    "CREATE INDEX IF NOT EXISTS idx_vitals_timestamp ON vitals(patient_id, timestamp)",
    """
    CREATE TABLE IF NOT EXISTS family_history (
        id              SERIAL PRIMARY KEY,
        patient_id      TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
        description     TEXT NOT NULL,
        created_at      TIMESTAMP NOT NULL DEFAULT NOW()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_family_history_patient ON family_history(patient_id)",
    """
    CREATE TABLE IF NOT EXISTS surgical_history (
        id              SERIAL PRIMARY KEY,
        patient_id      TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
        description     TEXT NOT NULL,
        created_at      TIMESTAMP NOT NULL DEFAULT NOW()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_surgical_history_patient ON surgical_history(patient_id)",
    """
    CREATE TABLE IF NOT EXISTS lifestyle (
        id              SERIAL PRIMARY KEY,
        patient_id      TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
        key             TEXT NOT NULL,
        value           TEXT NOT NULL,
        created_at      TIMESTAMP NOT NULL DEFAULT NOW()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_lifestyle_patient ON lifestyle(patient_id)",
    """
    CREATE TABLE IF NOT EXISTS genetic_markers (
        id              SERIAL PRIMARY KEY,
        patient_id      TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
        key             TEXT NOT NULL,
        value           TEXT NOT NULL,
        created_at      TIMESTAMP NOT NULL DEFAULT NOW()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_genetic_markers_patient ON genetic_markers(patient_id)",
    """
    CREATE TABLE IF NOT EXISTS consultations (
        id              SERIAL PRIMARY KEY,
        patient_id      TEXT REFERENCES patients(id) ON DELETE SET NULL,
        specialty       TEXT NOT NULL,
        complaints      TEXT NOT NULL,
        response        TEXT NOT NULL,
        date            TIMESTAMP NOT NULL DEFAULT NOW(),
        status          TEXT NOT NULL DEFAULT 'legacy',
        title           TEXT NOT NULL DEFAULT '',
        session_id      TEXT,
        created_at      TIMESTAMP NOT NULL DEFAULT NOW()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_consultations_patient ON consultations(patient_id)",
    "CREATE INDEX IF NOT EXISTS idx_consultations_specialty ON consultations(specialty)",
    "CREATE INDEX IF NOT EXISTS idx_consultations_date ON consultations(date)",
    """
    CREATE TABLE IF NOT EXISTS users (
        id              SERIAL PRIMARY KEY,
        username        TEXT UNIQUE NOT NULL,
        password_hash   TEXT NOT NULL,
        patient_id      TEXT REFERENCES patients(id),
        consent_personal_data   BOOLEAN NOT NULL DEFAULT FALSE,
        consent_medical_ai      BOOLEAN NOT NULL DEFAULT FALSE,
        consent_at              TIMESTAMP,
        created_at      TIMESTAMP NOT NULL DEFAULT NOW()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
    "CREATE INDEX IF NOT EXISTS idx_users_patient ON users(patient_id)",
    """
    CREATE TABLE IF NOT EXISTS documents (
        id              SERIAL PRIMARY KEY,
        patient_id      TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
        file_name       TEXT NOT NULL,
        file_type       TEXT NOT NULL DEFAULT '',
        file_size       INTEGER NOT NULL DEFAULT 0,
        content         BYTEA NOT NULL,
        notes           TEXT NOT NULL DEFAULT '',
        uploaded_at     TIMESTAMP NOT NULL DEFAULT NOW()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_documents_patient ON documents(patient_id)",
    """
    CREATE TABLE IF NOT EXISTS schema_version (
        version     INTEGER PRIMARY KEY,
        applied_at  TIMESTAMP NOT NULL DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS chat_messages (
        id              SERIAL PRIMARY KEY,
        consultation_id INTEGER NOT NULL REFERENCES consultations(id) ON DELETE CASCADE,
        role            TEXT NOT NULL CHECK(role IN ('user','assistant','system')),
        content         TEXT NOT NULL,
        metadata        TEXT NOT NULL DEFAULT '{}',
        created_at      TIMESTAMP NOT NULL DEFAULT NOW()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_chat_msg_consult ON chat_messages(consultation_id)",
    """
    CREATE TABLE IF NOT EXISTS chat_attachments (
        id              SERIAL PRIMARY KEY,
        consultation_id INTEGER NOT NULL REFERENCES consultations(id) ON DELETE CASCADE,
        message_id      INTEGER REFERENCES chat_messages(id) ON DELETE SET NULL,
        file_name       TEXT NOT NULL,
        file_type       TEXT NOT NULL,
        file_size       INTEGER NOT NULL,
        file_path       TEXT NOT NULL,
        created_at      TIMESTAMP NOT NULL DEFAULT NOW()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_chat_att_consult ON chat_attachments(consultation_id)",
    """
    CREATE TABLE IF NOT EXISTS audit_log (
        id              SERIAL PRIMARY KEY,
        timestamp       TIMESTAMP NOT NULL DEFAULT NOW(),
        level           TEXT NOT NULL DEFAULT 'INFO',
        category        TEXT NOT NULL DEFAULT 'general',
        action          TEXT NOT NULL,
        message         TEXT,
        entity_type     TEXT,
        entity_id       TEXT,
        actor_type      TEXT DEFAULT 'system',
        actor_id        TEXT,
        actor_name      TEXT,
        data            TEXT,
        request_id      TEXT,
        ip_address      TEXT,
        user_agent      TEXT
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp)",
    "CREATE INDEX IF NOT EXISTS idx_audit_log_action ON audit_log(action)",
    "CREATE INDEX IF NOT EXISTS idx_audit_log_category ON audit_log(category)",
    "CREATE INDEX IF NOT EXISTS idx_audit_log_entity ON audit_log(entity_type, entity_id)",
    "CREATE INDEX IF NOT EXISTS idx_audit_log_actor ON audit_log(actor_id)",
    """
    CREATE TABLE IF NOT EXISTS revoked_tokens (
        jti             TEXT PRIMARY KEY,
        user_id         INTEGER NOT NULL,
        revoked_at      TIMESTAMP NOT NULL DEFAULT NOW(),
        expires_at      TIMESTAMP NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_revoked_tokens_expires ON revoked_tokens(expires_at)",
]


def init_db() -> None:
    """Create all tables if they don't exist, then run migrations."""
    with engine.begin() as conn:
        for sql in _TABLES_SQL:
            conn.execute(text(sql))
        # Migrations: add columns that may not exist on older schemas
        _migrate_add_columns(conn)
    logger.info("Database initialized (PostgreSQL)")


def _migrate_add_columns(conn) -> None:
    """Add columns introduced after initial schema creation."""
    inspector = inspect(engine)
    user_cols = {c["name"] for c in inspector.get_columns("users")}
    if "consent_personal_data" not in user_cols:
        conn.execute(text("ALTER TABLE users ADD COLUMN consent_personal_data BOOLEAN NOT NULL DEFAULT FALSE"))
    if "consent_medical_ai" not in user_cols:
        conn.execute(text("ALTER TABLE users ADD COLUMN consent_medical_ai BOOLEAN NOT NULL DEFAULT FALSE"))
    if "consent_at" not in user_cols:
        conn.execute(text("ALTER TABLE users ADD COLUMN consent_at TIMESTAMP"))


# ══════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════

def _row_to_dict(row) -> dict:
    """Convert a SQLAlchemy Row/RowMapping to dict."""
    if row is None:
        return None
    if hasattr(row, '_mapping'):
        return dict(row._mapping)
    return dict(row)


def _parse_lab_value(raw: str) -> float | str:
    """Try to parse a lab value as float; return string if it fails."""
    try:
        return float(raw)
    except (ValueError, TypeError):
        return raw


# ══════════════════════════════════════════════════════════════
# Patient CRUD
# ══════════════════════════════════════════════════════════════

def save_patient(patient: Patient) -> str:
    """Insert or update a complete patient record atomically.
    Uses replace-all-children strategy within a transaction.
    Returns patient ID.
    """
    with engine.begin() as conn:
        # Upsert patient row
        conn.execute(
            text("""
                INSERT INTO patients (id, first_name, last_name, date_of_birth, gender, blood_type, notes, updated_at)
                VALUES (:id, :first_name, :last_name, :dob, :gender, :blood_type, :notes, NOW())
                ON CONFLICT(id) DO UPDATE SET
                    first_name=EXCLUDED.first_name, last_name=EXCLUDED.last_name,
                    date_of_birth=EXCLUDED.date_of_birth, gender=EXCLUDED.gender,
                    blood_type=EXCLUDED.blood_type, notes=EXCLUDED.notes,
                    updated_at=NOW()
            """),
            {
                "id": patient.id,
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "dob": patient.date_of_birth.isoformat(),
                "gender": patient.gender.value,
                "blood_type": patient.blood_type.value if patient.blood_type else None,
                "notes": encrypt_field(patient.notes),
            },
        )

        # Delete all child rows, then re-insert
        for table in (
            "allergies", "medications", "diagnoses", "lab_results",
            "vitals", "family_history", "surgical_history",
            "lifestyle", "genetic_markers",
        ):
            conn.execute(text(f"DELETE FROM {table} WHERE patient_id = :pid"), {"pid": patient.id})

        # Allergies
        for a in patient.allergies:
            conn.execute(
                text("INSERT INTO allergies (patient_id, substance, reaction, severity) VALUES (:pid, :sub, :react, :sev)"),
                {"pid": patient.id, "sub": a.substance, "react": a.reaction, "sev": a.severity},
            )

        # Medications
        for m in patient.medications:
            conn.execute(
                text("""INSERT INTO medications
                    (patient_id, name, dosage, frequency, route, start_date, end_date, prescribing_doctor, notes)
                    VALUES (:pid, :name, :dosage, :freq, :route, :start, :end, :doctor, :notes)"""),
                {
                    "pid": patient.id, "name": m.name, "dosage": m.dosage,
                    "freq": m.frequency, "route": m.route,
                    "start": m.start_date.isoformat() if m.start_date else None,
                    "end": m.end_date.isoformat() if m.end_date else None,
                    "doctor": m.prescribing_doctor, "notes": encrypt_field(m.notes),
                },
            )

        # Diagnoses
        for d in patient.diagnoses:
            conn.execute(
                text("""INSERT INTO diagnoses
                    (patient_id, icd10_code, name, date_diagnosed, status, notes, confidence)
                    VALUES (:pid, :icd, :name, :dd, :status, :notes, :conf)"""),
                {
                    "pid": patient.id, "icd": d.icd10_code, "name": d.name,
                    "dd": d.date_diagnosed.isoformat(), "status": d.status,
                    "notes": encrypt_field(d.notes), "conf": d.confidence,
                },
            )

        # Lab results
        for lr in patient.lab_results:
            conn.execute(
                text("""INSERT INTO lab_results
                    (patient_id, test_name, value, unit, reference_range, date, is_abnormal, notes)
                    VALUES (:pid, :test, :val, :unit, :ref, :dt, :abn, :notes)"""),
                {
                    "pid": patient.id, "test": lr.test_name, "val": str(lr.value),
                    "unit": lr.unit, "ref": lr.reference_range,
                    "dt": lr.date.isoformat(), "abn": 1 if lr.is_abnormal else 0,
                    "notes": encrypt_field(lr.notes),
                },
            )

        # Vitals
        for v in patient.vitals_history:
            conn.execute(
                text("""INSERT INTO vitals
                    (patient_id, timestamp, systolic_bp, diastolic_bp, heart_rate,
                     temperature, spo2, respiratory_rate, weight, height, blood_glucose)
                    VALUES (:pid, :ts, :sys, :dia, :hr, :temp, :spo2, :rr, :wt, :ht, :bg)"""),
                {
                    "pid": patient.id, "ts": v.timestamp.isoformat(),
                    "sys": v.systolic_bp, "dia": v.diastolic_bp, "hr": v.heart_rate,
                    "temp": v.temperature, "spo2": v.spo2, "rr": v.respiratory_rate,
                    "wt": v.weight, "ht": v.height, "bg": v.blood_glucose,
                },
            )

        # Family history
        for desc in patient.family_history:
            conn.execute(
                text("INSERT INTO family_history (patient_id, description) VALUES (:pid, :desc)"),
                {"pid": patient.id, "desc": encrypt_field(desc)},
            )

        # Surgical history
        for desc in patient.surgical_history:
            conn.execute(
                text("INSERT INTO surgical_history (patient_id, description) VALUES (:pid, :desc)"),
                {"pid": patient.id, "desc": encrypt_field(desc)},
            )

        # Lifestyle
        for k, v in patient.lifestyle.items():
            conn.execute(
                text("INSERT INTO lifestyle (patient_id, key, value) VALUES (:pid, :k, :v)"),
                {"pid": patient.id, "k": k, "v": encrypt_field(v)},
            )

        # Genetic markers
        for k, v in patient.genetic_markers.items():
            raw = json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v
            conn.execute(
                text("INSERT INTO genetic_markers (patient_id, key, value) VALUES (:pid, :k, :v)"),
                {"pid": patient.id, "k": k, "v": encrypt_field(raw)},
            )

    return patient.id


def load_patient(patient_id: str) -> Patient | None:
    """Load a complete Patient object with all related data."""
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT * FROM patients WHERE id = :id"), {"id": patient_id}
        ).mappings().first()
        if not row:
            return None

        pid = row["id"]

        # Allergies
        allergies = [
            Allergy(substance=r["substance"], reaction=r["reaction"], severity=r["severity"], id=r["id"])
            for r in conn.execute(
                text("SELECT * FROM allergies WHERE patient_id = :pid"), {"pid": pid}
            ).mappings()
        ]

        # Medications
        medications = [
            Medication(
                name=r["name"], dosage=r["dosage"], frequency=r["frequency"],
                route=r["route"],
                start_date=date.fromisoformat(r["start_date"]) if r["start_date"] else None,
                end_date=date.fromisoformat(r["end_date"]) if r["end_date"] else None,
                prescribing_doctor=r["prescribing_doctor"], notes=decrypt_field(r["notes"]),
                id=r["id"],
            )
            for r in conn.execute(
                text("SELECT * FROM medications WHERE patient_id = :pid"), {"pid": pid}
            ).mappings()
        ]

        # Diagnoses
        diagnoses = [
            Diagnosis(
                icd10_code=r["icd10_code"], name=r["name"],
                date_diagnosed=date.fromisoformat(r["date_diagnosed"]),
                status=r["status"], notes=decrypt_field(r["notes"]), confidence=r["confidence"],
                id=r["id"],
            )
            for r in conn.execute(
                text("SELECT * FROM diagnoses WHERE patient_id = :pid"), {"pid": pid}
            ).mappings()
        ]

        # Lab results
        lab_results = [
            LabResult(
                test_name=r["test_name"],
                value=_parse_lab_value(r["value"]),
                unit=r["unit"], reference_range=r["reference_range"],
                date=date.fromisoformat(r["date"]),
                is_abnormal=bool(r["is_abnormal"]), notes=decrypt_field(r["notes"]),
                id=r["id"],
            )
            for r in conn.execute(
                text("SELECT * FROM lab_results WHERE patient_id = :pid ORDER BY date"), {"pid": pid}
            ).mappings()
        ]

        # Vitals
        vitals_history = [
            VitalSigns(
                id=r["id"],
                timestamp=datetime.fromisoformat(r["timestamp"]),
                systolic_bp=r["systolic_bp"], diastolic_bp=r["diastolic_bp"],
                heart_rate=r["heart_rate"], temperature=r["temperature"],
                spo2=r["spo2"], respiratory_rate=r["respiratory_rate"],
                weight=r["weight"], height=r["height"],
                blood_glucose=r["blood_glucose"],
            )
            for r in conn.execute(
                text("SELECT * FROM vitals WHERE patient_id = :pid ORDER BY timestamp"), {"pid": pid}
            ).mappings()
        ]

        # Simple lists
        family_history = [
            decrypt_field(r["description"]) or ""
            for r in conn.execute(
                text("SELECT description FROM family_history WHERE patient_id = :pid"), {"pid": pid}
            ).mappings()
        ]
        surgical_history = [
            decrypt_field(r["description"]) or ""
            for r in conn.execute(
                text("SELECT description FROM surgical_history WHERE patient_id = :pid"), {"pid": pid}
            ).mappings()
        ]

        # Key-value dicts
        lifestyle = {
            r["key"]: decrypt_field(r["value"]) or ""
            for r in conn.execute(
                text("SELECT key, value FROM lifestyle WHERE patient_id = :pid"), {"pid": pid}
            ).mappings()
        }
        genetic_markers: dict[str, Any] = {}
        for r in conn.execute(
            text("SELECT key, value FROM genetic_markers WHERE patient_id = :pid"), {"pid": pid}
        ).mappings():
            raw = decrypt_field(r["value"]) or ""
            try:
                genetic_markers[r["key"]] = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                genetic_markers[r["key"]] = raw

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
            notes=decrypt_field(row["notes"]),
        )


def list_patients() -> list[dict[str, str]]:
    """Return summary list of all patients."""
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT id, first_name, last_name, date_of_birth, gender FROM patients ORDER BY last_name")
        ).mappings().all()
        return [
            {
                "id": r["id"],
                "name": f"{r['last_name'] or ''} {r['first_name'] or ''}".strip() or "Без имени",
                "dob": r["date_of_birth"],
                "gender": r["gender"],
            }
            for r in rows
        ]


def delete_patient(patient_id: str) -> bool:
    """Delete a patient and all related data (cascade). Returns True if deleted."""
    with engine.begin() as conn:
        result = conn.execute(
            text("DELETE FROM patients WHERE id = :id"), {"id": patient_id}
        )
    return result.rowcount > 0


# ══════════════════════════════════════════════════════════════
# Granular insert operations
# ══════════════════════════════════════════════════════════════

def _check_patient_exists(conn, patient_id: str) -> None:
    """Raise ValueError if patient does not exist."""
    row = conn.execute(
        text("SELECT 1 FROM patients WHERE id = :id"), {"id": patient_id}
    ).first()
    if not row:
        raise ValueError(f"Пациент {patient_id} не найден")


def add_vitals(patient_id: str, vitals: VitalSigns) -> int:
    """Insert a single vitals record. Returns the new row ID."""
    with engine.begin() as conn:
        _check_patient_exists(conn, patient_id)
        result = conn.execute(
            text("""INSERT INTO vitals
                (patient_id, timestamp, systolic_bp, diastolic_bp, heart_rate,
                 temperature, spo2, respiratory_rate, weight, height, blood_glucose)
                VALUES (:pid, :ts, :sys, :dia, :hr, :temp, :spo2, :rr, :wt, :ht, :bg)
                RETURNING id"""),
            {
                "pid": patient_id, "ts": vitals.timestamp.isoformat(),
                "sys": vitals.systolic_bp, "dia": vitals.diastolic_bp,
                "hr": vitals.heart_rate, "temp": vitals.temperature,
                "spo2": vitals.spo2, "rr": vitals.respiratory_rate,
                "wt": vitals.weight, "ht": vitals.height, "bg": vitals.blood_glucose,
            },
        )
        row_id = result.scalar()
        conn.execute(
            text("UPDATE patients SET updated_at = NOW() WHERE id = :pid"),
            {"pid": patient_id},
        )
    return row_id


def add_lab_result(patient_id: str, lab_result: LabResult) -> int:
    """Insert a single lab result. Returns the new row ID."""
    with engine.begin() as conn:
        _check_patient_exists(conn, patient_id)
        result = conn.execute(
            text("""INSERT INTO lab_results
                (patient_id, test_name, value, unit, reference_range, date, is_abnormal, notes)
                VALUES (:pid, :test, :val, :unit, :ref, :dt, :abn, :notes)
                RETURNING id"""),
            {
                "pid": patient_id, "test": lab_result.test_name,
                "val": str(lab_result.value), "unit": lab_result.unit,
                "ref": lab_result.reference_range, "dt": lab_result.date.isoformat(),
                "abn": 1 if lab_result.is_abnormal else 0, "notes": encrypt_field(lab_result.notes),
            },
        )
        row_id = result.scalar()
        conn.execute(
            text("UPDATE patients SET updated_at = NOW() WHERE id = :pid"),
            {"pid": patient_id},
        )
    return row_id


def add_diagnosis(patient_id: str, diagnosis: Diagnosis) -> int:
    """Insert a single diagnosis. Returns the new row ID."""
    with engine.begin() as conn:
        _check_patient_exists(conn, patient_id)
        result = conn.execute(
            text("""INSERT INTO diagnoses
                (patient_id, icd10_code, name, date_diagnosed, status, notes, confidence)
                VALUES (:pid, :icd, :name, :dd, :status, :notes, :conf)
                RETURNING id"""),
            {
                "pid": patient_id, "icd": diagnosis.icd10_code,
                "name": diagnosis.name, "dd": diagnosis.date_diagnosed.isoformat(),
                "status": diagnosis.status, "notes": encrypt_field(diagnosis.notes),
                "conf": diagnosis.confidence,
            },
        )
        row_id = result.scalar()
        conn.execute(
            text("UPDATE patients SET updated_at = NOW() WHERE id = :pid"),
            {"pid": patient_id},
        )
    return row_id


def add_medication(patient_id: str, medication: Medication) -> int:
    """Insert a single medication. Returns the new row ID."""
    with engine.begin() as conn:
        _check_patient_exists(conn, patient_id)
        result = conn.execute(
            text("""INSERT INTO medications
                (patient_id, name, dosage, frequency, route, start_date, end_date, prescribing_doctor, notes)
                VALUES (:pid, :name, :dosage, :freq, :route, :start, :end, :doctor, :notes)
                RETURNING id"""),
            {
                "pid": patient_id, "name": medication.name,
                "dosage": medication.dosage, "freq": medication.frequency,
                "route": medication.route,
                "start": medication.start_date.isoformat() if medication.start_date else None,
                "end": medication.end_date.isoformat() if medication.end_date else None,
                "doctor": medication.prescribing_doctor, "notes": encrypt_field(medication.notes),
            },
        )
        row_id = result.scalar()
        conn.execute(
            text("UPDATE patients SET updated_at = NOW() WHERE id = :pid"),
            {"pid": patient_id},
        )
    return row_id


def add_allergy(patient_id: str, allergy: Allergy) -> int:
    """Insert a single allergy. Returns the new row ID."""
    with engine.begin() as conn:
        _check_patient_exists(conn, patient_id)
        result = conn.execute(
            text("INSERT INTO allergies (patient_id, substance, reaction, severity) VALUES (:pid, :sub, :react, :sev) RETURNING id"),
            {"pid": patient_id, "sub": allergy.substance, "react": allergy.reaction, "sev": allergy.severity},
        )
        row_id = result.scalar()
        conn.execute(
            text("UPDATE patients SET updated_at = NOW() WHERE id = :pid"),
            {"pid": patient_id},
        )
    return row_id


# ══════════════════════════════════════════════════════════════
# Generic sub-record delete / update
# ══════════════════════════════════════════════════════════════

_SUB_TABLES = {"allergies", "medications", "diagnoses", "lab_results", "vitals"}


def delete_sub_record(patient_id: str, table: str, record_id: int) -> bool:
    """Delete a single sub-record by ID, verifying patient ownership."""
    if table not in _SUB_TABLES:
        raise ValueError(f"Недопустимая таблица: {table}")
    with engine.begin() as conn:
        result = conn.execute(
            text(f"DELETE FROM {table} WHERE id = :rid AND patient_id = :pid"),
            {"rid": record_id, "pid": patient_id},
        )
        if result.rowcount > 0:
            conn.execute(
                text("UPDATE patients SET updated_at = NOW() WHERE id = :pid"),
                {"pid": patient_id},
            )
            return True
    return False


def update_sub_record(patient_id: str, table: str, record_id: int, fields: dict) -> bool:
    """Update specific columns of a sub-record by ID, verifying patient ownership."""
    if table not in _SUB_TABLES:
        raise ValueError(f"Недопустимая таблица: {table}")
    if not fields:
        return False

    # Get valid column names from table via SQLAlchemy inspect
    with engine.connect() as conn:
        inspector = inspect(engine)
        columns = {col["name"] for col in inspector.get_columns(table)}
        valid_cols = columns - {"id", "patient_id", "created_at"}
        filtered = {k: v for k, v in fields.items() if k in valid_cols}
        if not filtered:
            return False

    # Encrypt notes/description fields
    if "notes" in filtered:
        filtered["notes"] = encrypt_field(filtered["notes"])
    if "description" in filtered:
        filtered["description"] = encrypt_field(filtered["description"])

    set_clause = ", ".join(f"{col} = :{col}" for col in filtered)
    params = dict(filtered)
    params["rid"] = record_id
    params["pid"] = patient_id

    with engine.begin() as conn:
        result = conn.execute(
            text(f"UPDATE {table} SET {set_clause} WHERE id = :rid AND patient_id = :pid"),
            params,
        )
        if result.rowcount > 0:
            conn.execute(
                text("UPDATE patients SET updated_at = NOW() WHERE id = :pid"),
                {"pid": patient_id},
            )
            return True
    return False


def update_patient_fields(patient_id: str, fields: dict) -> bool:
    """Update core patient fields directly."""
    allowed = {"first_name", "last_name", "date_of_birth", "gender", "blood_type", "notes"}
    filtered = {k: v for k, v in fields.items() if k in allowed}
    if not filtered:
        return False
    # Encrypt notes field if present
    if "notes" in filtered:
        filtered["notes"] = encrypt_field(filtered["notes"])
    set_clause = ", ".join(f"{col} = :{col}" for col in filtered)
    params = dict(filtered)
    params["pid"] = patient_id
    with engine.begin() as conn:
        result = conn.execute(
            text(f"UPDATE patients SET {set_clause}, updated_at = NOW() WHERE id = :pid"),
            params,
        )
    return result.rowcount > 0


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
    with engine.begin() as conn:
        result = conn.execute(
            text("""INSERT INTO consultations (patient_id, specialty, complaints, response)
                VALUES (:pid, :spec, :comp, :resp) RETURNING id"""),
            {
                "pid": patient_id, "spec": specialty,
                "comp": encrypt_field(complaints),
                "resp": encrypt_field(json.dumps(response, ensure_ascii=False)),
            },
        )
    return result.scalar()


def get_consultation_history(
    patient_id: str | None = None,
    specialty: str | None = None,
    limit: int = 50,
) -> list[dict]:
    """Retrieve consultation history filtered by patient and/or specialty."""
    clauses = []
    params: dict = {}

    if patient_id:
        clauses.append("c.patient_id = :pid")
        params["pid"] = patient_id
    if specialty:
        clauses.append("c.specialty = :spec")
        params["spec"] = specialty

    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    params["lim"] = limit

    with engine.connect() as conn:
        rows = conn.execute(
            text(f"""SELECT c.id, c.patient_id, c.specialty, c.complaints, c.response, c.date,
                        p.first_name, p.last_name
                    FROM consultations c
                    LEFT JOIN patients p ON c.patient_id = p.id
                    {where}
                    ORDER BY c.date DESC
                    LIMIT :lim"""),
            params,
        ).mappings().all()

    results = []
    for r in rows:
        entry = {
            "id": r["id"],
            "patient_id": r["patient_id"],
            "patient_name": (
                f"{r['last_name'] or ''} {r['first_name'] or ''}".strip() or None
            ) if r["patient_id"] else None,
            "specialty": r["specialty"],
            "complaints": decrypt_field(r["complaints"]),
            "date": r["date"].isoformat() if isinstance(r["date"], datetime) else r["date"],
        }
        try:
            entry["response"] = json.loads(decrypt_field(r["response"]) or "{}")
        except (json.JSONDecodeError, TypeError):
            entry["response"] = decrypt_field(r["response"])
        results.append(entry)

    return results


# ══════════════════════════════════════════════════════════════
# Query / analytics operations
# ══════════════════════════════════════════════════════════════

def get_lab_trends(patient_id: str, test_name: str, limit: int = 20) -> list[dict]:
    """Get historical lab results for a specific test, ordered by date ascending."""
    with engine.connect() as conn:
        rows = conn.execute(
            text("""SELECT test_name, value, unit, reference_range, date, is_abnormal, notes
                FROM lab_results
                WHERE patient_id = :pid AND LOWER(test_name) LIKE LOWER(:pattern)
                ORDER BY date ASC
                LIMIT :lim"""),
            {"pid": patient_id, "pattern": f"%{test_name}%", "lim": limit},
        ).mappings().all()

    return [
        {
            "test_name": r["test_name"],
            "value": _parse_lab_value(r["value"]),
            "unit": r["unit"],
            "reference_range": r["reference_range"],
            "date": r["date"],
            "is_abnormal": bool(r["is_abnormal"]),
            "notes": decrypt_field(r["notes"]),
        }
        for r in rows
    ]


def get_vitals_trends(patient_id: str, limit: int = 20) -> list[dict]:
    """Get historical vitals records ordered by timestamp descending."""
    with engine.connect() as conn:
        rows = conn.execute(
            text("""SELECT timestamp, systolic_bp, diastolic_bp, heart_rate, temperature,
                      spo2, respiratory_rate, weight, height, blood_glucose
                FROM vitals
                WHERE patient_id = :pid
                ORDER BY timestamp DESC
                LIMIT :lim"""),
            {"pid": patient_id, "lim": limit},
        ).mappings().all()

    return [dict(r) for r in rows]


def search_patients(query: str) -> list[dict[str, str]]:
    """Search patients by name (partial match). PostgreSQL LOWER supports Unicode."""
    with engine.connect() as conn:
        rows = conn.execute(
            text("""SELECT id, first_name, last_name, date_of_birth, gender
                FROM patients
                WHERE LOWER(first_name) LIKE LOWER(:pattern) OR LOWER(last_name) LIKE LOWER(:pattern)
                ORDER BY last_name"""),
            {"pattern": f"%{query}%"},
        ).mappings().all()

    return [
        {
            "id": r["id"],
            "name": f"{r['last_name'] or ''} {r['first_name'] or ''}".strip() or "Без имени",
            "dob": r["date_of_birth"],
            "gender": r["gender"],
        }
        for r in rows
    ]


def get_patients_by_diagnosis(icd10_prefix: str) -> list[dict]:
    """Find all patients with a diagnosis matching an ICD-10 prefix."""
    with engine.connect() as conn:
        rows = conn.execute(
            text("""SELECT DISTINCT p.id AS patient_id,
                      COALESCE(p.last_name, '') || ' ' || COALESCE(p.first_name, '') AS patient_name,
                      d.name AS diagnosis, d.icd10_code, d.status
                FROM diagnoses d
                JOIN patients p ON d.patient_id = p.id
                WHERE d.icd10_code LIKE :pattern
                ORDER BY p.last_name"""),
            {"pattern": f"{icd10_prefix}%"},
        ).mappings().all()

    return [dict(r) for r in rows]


# ══════════════════════════════════════════════════════════════
# User management
# ══════════════════════════════════════════════════════════════

def create_user(
    username: str,
    password_hash: str,
    patient_id: str | None = None,
    consent_personal_data: bool = False,
    consent_medical_ai: bool = False,
) -> int:
    """Create a new user. Returns user ID."""
    with engine.begin() as conn:
        result = conn.execute(
            text(
                "INSERT INTO users (username, password_hash, patient_id, "
                "consent_personal_data, consent_medical_ai, consent_at) "
                "VALUES (:u, :ph, :pid, :cpd, :cma, NOW()) RETURNING id"
            ),
            {
                "u": username, "ph": password_hash, "pid": patient_id,
                "cpd": consent_personal_data, "cma": consent_medical_ai,
            },
        )
    return result.scalar()


def get_user_by_username(username: str) -> dict | None:
    """Fetch user by username. Returns dict or None."""
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT id, username, password_hash, patient_id, created_at FROM users WHERE username = :u"),
            {"u": username},
        ).mappings().first()
    return dict(row) if row else None


def get_user_by_id(user_id: int) -> dict | None:
    """Fetch user by ID. Returns dict or None."""
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT id, username, password_hash, patient_id, created_at FROM users WHERE id = :id"),
            {"id": user_id},
        ).mappings().first()
    return dict(row) if row else None


def link_user_to_patient(user_id: int, patient_id: str) -> None:
    """Link user account to a patient record."""
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE users SET patient_id = :pid WHERE id = :uid"),
            {"pid": patient_id, "uid": user_id},
        )


def update_user_password(user_id: int, new_hash: str) -> bool:
    """Update password hash for a user. Returns True if updated."""
    with engine.begin() as conn:
        result = conn.execute(
            text("UPDATE users SET password_hash = :ph WHERE id = :uid"),
            {"ph": new_hash, "uid": user_id},
        )
    return result.rowcount > 0


def delete_user(user_id: int) -> bool:
    """Delete a user account (patient record preserved). Returns True if deleted."""
    with engine.begin() as conn:
        result = conn.execute(
            text("DELETE FROM users WHERE id = :uid"), {"uid": user_id}
        )
    return result.rowcount > 0


# ══════════════════════════════════════════════════════════════
# Token revocation (refresh token jti blocklist)
# ══════════════════════════════════════════════════════════════

def revoke_token(jti: str, user_id: int, expires_at: datetime) -> None:
    """Add a refresh token's jti to the revocation list."""
    with engine.begin() as conn:
        conn.execute(
            text("""INSERT INTO revoked_tokens (jti, user_id, expires_at)
                VALUES (:jti, :uid, :exp) ON CONFLICT (jti) DO NOTHING"""),
            {"jti": jti, "uid": user_id, "exp": expires_at},
        )


def is_token_revoked(jti: str) -> bool:
    """Check if a refresh token jti has been revoked."""
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT 1 FROM revoked_tokens WHERE jti = :jti"),
            {"jti": jti},
        ).fetchone()
    return row is not None


def cleanup_expired_tokens() -> int:
    """Remove expired revoked tokens (cleanup job). Returns count of removed rows."""
    with engine.begin() as conn:
        result = conn.execute(
            text("DELETE FROM revoked_tokens WHERE expires_at < NOW()"),
        )
    return result.rowcount


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
    with engine.begin() as conn:
        _check_patient_exists(conn, patient_id)
        result = conn.execute(
            text("""INSERT INTO documents (patient_id, file_name, file_type, file_size, content, notes)
                VALUES (:pid, :fn, :ft, :fs, :content, :notes) RETURNING id"""),
            {"pid": patient_id, "fn": file_name, "ft": file_type, "fs": file_size, "content": content, "notes": encrypt_field(notes)},
        )
    return result.scalar()


def list_documents(patient_id: str) -> list[dict]:
    """List documents for a patient (without BLOB content)."""
    with engine.connect() as conn:
        rows = conn.execute(
            text("""SELECT id, file_name, file_type, file_size, notes, uploaded_at
                FROM documents WHERE patient_id = :pid ORDER BY uploaded_at DESC"""),
            {"pid": patient_id},
        ).mappings().all()
    docs = [dict(r) for r in rows]
    for d in docs:
        d["notes"] = decrypt_field(d.get("notes"))
    return docs


def get_document(doc_id: int) -> dict | None:
    """Fetch a single document with its content."""
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT id, patient_id, file_name, file_type, file_size, content, notes, uploaded_at FROM documents WHERE id = :id"),
            {"id": doc_id},
        ).mappings().first()
    if not row:
        return None
    result = dict(row)
    # Ensure content is bytes (PostgreSQL BYTEA returns memoryview)
    if isinstance(result.get("content"), memoryview):
        result["content"] = bytes(result["content"])
    result["notes"] = decrypt_field(result.get("notes"))
    return result


def delete_document(doc_id: int) -> bool:
    """Delete a document by ID. Returns True if deleted."""
    with engine.begin() as conn:
        result = conn.execute(
            text("DELETE FROM documents WHERE id = :id"), {"id": doc_id}
        )
    return result.rowcount > 0


# ══════════════════════════════════════════════════════════════
# Chat consultations
# ══════════════════════════════════════════════════════════════

def create_chat_consultation(
    patient_id: str | None,
    specialty: str,
    complaints: str,
    session_id: str,
    title: str = "",
) -> int:
    """Create a new chat-style consultation. Returns consultation ID."""
    with engine.begin() as conn:
        result = conn.execute(
            text("""INSERT INTO consultations
                (patient_id, specialty, complaints, response, status, title, session_id)
                VALUES (:pid, :spec, :comp, '{}', 'active', :title, :sid)
                RETURNING id"""),
            {"pid": patient_id, "spec": specialty, "comp": encrypt_field(complaints), "title": title, "sid": session_id},
        )
    return result.scalar()


def add_chat_message(
    consultation_id: int,
    role: str,
    content: str,
    metadata: dict | None = None,
) -> int:
    """Add a chat message. Returns message ID."""
    with engine.begin() as conn:
        result = conn.execute(
            text("""INSERT INTO chat_messages (consultation_id, role, content, metadata)
                VALUES (:cid, :role, :content, :meta) RETURNING id"""),
            {
                "cid": consultation_id, "role": role, "content": encrypt_field(content),
                "meta": json.dumps(metadata or {}, ensure_ascii=False),
            },
        )
    return result.scalar()


def get_chat_messages(consultation_id: int) -> list[dict]:
    """Get all messages for a consultation, ordered chronologically."""
    with engine.connect() as conn:
        rows = conn.execute(
            text("""SELECT m.id, m.consultation_id, m.role, m.content, m.metadata, m.created_at
                FROM chat_messages m
                WHERE m.consultation_id = :cid
                ORDER BY m.created_at ASC, m.id ASC"""),
            {"cid": consultation_id},
        ).mappings().all()

        results = []
        for r in rows:
            entry = dict(r)
            # Decrypt content
            entry["content"] = decrypt_field(entry.get("content"))
            # Convert datetime to string for JSON serialization
            if isinstance(entry.get("created_at"), datetime):
                entry["created_at"] = entry["created_at"].isoformat()
            try:
                entry["metadata"] = json.loads(r["metadata"])
            except (json.JSONDecodeError, TypeError):
                entry["metadata"] = {}
            # Attach attachments for this message
            atts = conn.execute(
                text("""SELECT id, file_name, file_type, file_size, created_at
                    FROM chat_attachments WHERE message_id = :mid"""),
                {"mid": r["id"]},
            ).mappings().all()
            entry["attachments"] = [dict(a) for a in atts]
            results.append(entry)
    return results


def save_chat_attachment(
    consultation_id: int,
    message_id: int | None,
    file_name: str,
    file_type: str,
    file_size: int,
    file_path: str,
) -> int:
    """Save a chat attachment record. Returns attachment ID."""
    with engine.begin() as conn:
        result = conn.execute(
            text("""INSERT INTO chat_attachments
                (consultation_id, message_id, file_name, file_type, file_size, file_path)
                VALUES (:cid, :mid, :fn, :ft, :fs, :fp) RETURNING id"""),
            {"cid": consultation_id, "mid": message_id, "fn": file_name, "ft": file_type, "fs": file_size, "fp": file_path},
        )
    return result.scalar()


def get_chat_attachment(attachment_id: int) -> dict | None:
    """Get a single attachment by ID."""
    with engine.connect() as conn:
        row = conn.execute(
            text("""SELECT id, consultation_id, message_id, file_name, file_type, file_size, file_path, created_at
                FROM chat_attachments WHERE id = :id"""),
            {"id": attachment_id},
        ).mappings().first()
    return dict(row) if row else None


def get_consultation_by_id(consultation_id: int) -> dict | None:
    """Get consultation metadata by ID."""
    with engine.connect() as conn:
        row = conn.execute(
            text("""SELECT c.id, c.patient_id, c.specialty, c.complaints, c.response,
                      c.date, c.status, c.title, c.session_id,
                      p.first_name, p.last_name
                FROM consultations c
                LEFT JOIN patients p ON c.patient_id = p.id
                WHERE c.id = :cid"""),
            {"cid": consultation_id},
        ).mappings().first()
    if not row:
        return None
    entry = dict(row)
    entry["complaints"] = decrypt_field(entry.get("complaints"))
    # Convert datetime to string
    if isinstance(entry.get("date"), datetime):
        entry["date"] = entry["date"].isoformat()
    try:
        decrypted_resp = decrypt_field(row["response"]) if row["response"] else "{}"
        entry["response"] = json.loads(decrypted_resp or "{}")
    except (json.JSONDecodeError, TypeError):
        entry["response"] = {}
    return entry


def get_patient_chat_consultations(patient_id: str, limit: int = 50) -> list[dict]:
    """Get chat consultations for a patient with last message preview."""
    with engine.connect() as conn:
        rows = conn.execute(
            text("""SELECT c.id, c.specialty, c.complaints, c.date, c.status, c.title, c.session_id,
                      (SELECT content FROM chat_messages
                       WHERE consultation_id = c.id ORDER BY created_at DESC, id DESC LIMIT 1) AS last_message,
                      (SELECT COUNT(*) FROM chat_messages WHERE consultation_id = c.id) AS message_count
                FROM consultations c
                WHERE c.patient_id = :pid
                ORDER BY c.date DESC
                LIMIT :lim"""),
            {"pid": patient_id, "lim": limit},
        ).mappings().all()
    results = []
    for r in rows:
        entry = dict(r)
        entry["complaints"] = decrypt_field(entry.get("complaints"))
        entry["last_message"] = decrypt_field(entry.get("last_message"))
        if isinstance(entry.get("date"), datetime):
            entry["date"] = entry["date"].isoformat()
        results.append(entry)
    return results


def close_consultation(consultation_id: int) -> bool:
    """Close a consultation. Returns True if updated."""
    with engine.begin() as conn:
        result = conn.execute(
            text("UPDATE consultations SET status = 'closed' WHERE id = :cid AND status = 'active'"),
            {"cid": consultation_id},
        )
    return result.rowcount > 0


# ══════════════════════════════════════════════════════════════
# Migration from JSON (legacy)
# ══════════════════════════════════════════════════════════════

def migrate_from_json(json_dir: str) -> dict:
    """Read all JSON patient files and insert them into the database."""
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
