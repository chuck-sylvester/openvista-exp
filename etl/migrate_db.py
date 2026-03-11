"""OpenVistA — Migrate JSON data to PostgreSQL.

Reads VistA VEHU JSON exports and loads them into PostgreSQL tables.
Idempotent: drops and recreates tables on each run.

Usage:
  python -m etl.migrate_db
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from sqlalchemy import text

from etl.db import (
    adt_movements, allergies, appointments, consults, create_tables, drop_tables, engine, exams, health_factors,
    immunizations, lab_results, labs, metadata, notes, orders, patient_education, patients, prescriptions,
    problems, procedures, rad_reports, skin_tests, surgeries, visit_diagnoses, visit_providers, vitals,
)

# Import 'settings' object from root-level config file
from config import settings

print("\n      Path:", Path(__file__))

DATA_DIR = Path(__file__).parent.parent / "input"
print(f"  DATA_DIR: {DATA_DIR}\n")

BATCH_SIZE = 500


def load_json(name: str) -> list[dict]:
    p = DATA_DIR / name
    if p.exists():
        return json.loads(p.read_text())
    print(f"  WARN: {p} not found")
    return []


def safe_int(val, default=None):
    if val is None:
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def migrate_patients(conn):
    data = load_json("patients.json")
    rows = []
    for p in data:
        dfn = safe_int(p.get("dfn"))
        if dfn is None:
            continue
        rows.append({
            "dfn": dfn,
            "name": p.get("name", ""),
            "sex": p.get("sex"),
            "dob": p.get("dob"),
            "ssn": p.get("ssn"),
            "street_1": p.get("street_1"),
            "street_2": p.get("street_2"),
            "city": p.get("city"),
            "state": p.get("state"),
            "zip": p.get("zip"),
            "phone_home": p.get("phone_home"),
            "phone_work": p.get("phone_work"),
            "phone_cell": p.get("phone_cell"),
            "email": p.get("email"),
            "marital_status": p.get("marital_status"),
            "religion": p.get("religion"),
            "occupation": p.get("occupation"),
            "veteran": bool(p.get("veteran")),
            "service_connected": bool(p.get("service_connected")),
            "sc_percentage": safe_int(p.get("sc_percentage")),
            "date_entered": p.get("date_entered"),
            "who_entered": p.get("who_entered"),
        })
    for i in range(0, len(rows), BATCH_SIZE):
        conn.execute(patients.insert(), rows[i:i + BATCH_SIZE])
    return len(rows)


def migrate_table(conn, table, json_file: str, pk_field: str, field_map: dict):
    """Generic migration for patient-linked tables."""
    data = load_json(json_file)
    patient_dfns = {r[0] for r in conn.execute(patients.select().with_only_columns(patients.c.dfn)).fetchall()}
    has_patient_fk = "patient_dfn" in field_map
    rows = []
    skipped = 0
    for rec in data:
        pk = safe_int(rec.get(pk_field))
        if pk is None:
            skipped += 1
            continue
        pt_dfn = safe_int(rec.get("patient_dfn"))
        if has_patient_fk and (pt_dfn is None or pt_dfn not in patient_dfns):
            skipped += 1
            continue
        row = {}
        for db_col, src_key in field_map.items():
            val = rec.get(src_key)
            row[db_col] = val
        row[pk_field] = pk
        rows.append(row)
    for i in range(0, len(rows), BATCH_SIZE):
        conn.execute(table.insert(), rows[i:i + BATCH_SIZE])
    return len(rows), skipped


def main():
    print("OpenVistA — Database Migration")
    print(f"Data source: {DATA_DIR}")
    print(f"Database: {engine.url}\n")

    t0 = time.time()

    print("Dropping existing tables...")
    drop_tables()
    print("Creating tables...")
    create_tables()

    with engine.begin() as conn:
        n = migrate_patients(conn)
        print(f"  patients:       {n:>7,} rows")

        n, s = migrate_table(conn, problems, "problems.json", "ifn", {
            "patient_dfn": "patient_dfn",
            "narrative_ptr": "narrative_ptr",
            "diagnosis_ptr": "diagnosis_ptr",
            "status": "status",
            "date_onset": "date_onset",
            "date_entered": "date_entered",
            "date_recorded": "date_recorded",
            "date_modified": "date_modified",
            "date_resolved": "date_resolved",
            "priority": "priority",
            "condition": "condition",
            "responsible_provider": "responsible_provider",
            "recording_provider": "recording_provider",
            "initial_provider": "initial_provider",
            "problem_number": "problem_number",
            "lexicon_term": "lexicon_term",
            "clinic": "clinic",
            "service": "service",
            "facility": "facility",
            "sc": "sc", "ao": "ao", "ir": "ir", "ec": "ec",
        })
        print(f"  problems:       {n:>7,} rows  ({s} skipped)")

        n, s = migrate_table(conn, allergies, "allergies.json", "ien", {
            "patient_dfn": "patient_dfn",
            "reactant": "reactant",
            "gmr_allergy_ptr": "gmr_allergy_ptr",
            "allergy_type": "allergy_type",
            "mechanism": "mechanism",
            "origination_date": "origination_date",
            "originator": "originator",
            "verified": "verified",
        })
        print(f"  allergies:      {n:>7,} rows  ({s} skipped)")

        n, s = migrate_table(conn, vitals, "vitals.json", "ien", {
            "patient_dfn": "patient_dfn",
            "vital_type": "vital_type",
            "rate": "rate",
            "date_taken": "date_taken",
            "date_entered": "date_entered",
            "hospital_location": "hospital_location",
            "entered_by": "entered_by",
        })
        print(f"  vitals:         {n:>7,} rows  ({s} skipped)")

        n, s = migrate_table(conn, prescriptions, "prescriptions.json", "ien", {
            "patient_dfn": "patient_dfn",
            "drug": "drug",
            "qty": "qty",
            "days_supply": "days_supply",
            "num_refills": "num_refills",
            "refills_remaining": "refills_remaining",
            "fill_date": "fill_date",
            "status": "status",
            "provider": "provider",
            "patient_status": "patient_status",
            "sig_code": "sig_code",
        })
        print(f"  prescriptions:  {n:>7,} rows  ({s} skipped)")

        n, s = migrate_table(conn, orders, "orders.json", "ien", {
            "patient_dfn": "patient_dfn",
            "order_status": "order_status",
            "when_entered": "when_entered",
            "start_date": "start_date",
            "stop_date": "stop_date",
            "entered_by": "entered_by",
            "current_location": "current_location",
            "nature_of_order": "nature_of_order",
            "object_of_order": "object_of_order",
            "package_ref": "package_ref",
            "current_agent": "current_agent",
            "replacing_order": "replacing_order",
            "date_released": "date_released",
            "elapse_event": "elapse_event",
        })
        print(f"  orders:         {n:>7,} rows  ({s} skipped)")

        n, s = migrate_table(conn, notes, "notes.json", "ien", {
            "patient_dfn": "patient_dfn",
            "document_type": "document_type",
            "status": "status",
            "episode_date": "episode_date",
            "entry_date": "entry_date",
            "author": "author",
            "expected_signer": "expected_signer",
            "attending": "attending",
            "signed_by": "signed_by",
            "signature_date": "signature_date",
            "signature_status": "signature_status",
            "hospital_location": "hospital_location",
            "visit": "visit",
            "parent_document": "parent_document",
            "body": "body",
        })
        print(f"  notes:          {n:>7,} rows  ({s} skipped)")

        n, s = migrate_table(conn, consults, "consults.json", "ien", {
            "patient_dfn": "patient_dfn",
            "date_entered": "date_entered",
            "order_ref": "order_ref",
            "patient_location": "patient_location",
            "to_service": "to_service",
            "from_location": "from_location",
            "date_requested": "date_requested",
            "procedure_type": "procedure_type",
            "urgency": "urgency",
            "place_of_consultation": "place_of_consultation",
            "attention": "attention",
            "cprs_status": "cprs_status",
            "last_action": "last_action",
            "sending_provider": "sending_provider",
            "result": "result",
            "mode_of_entry": "mode_of_entry",
        })
        print(f"  consults:       {n:>7,} rows  ({s} skipped)")

        n, s = migrate_table(conn, labs, "labs.json", "ien", {
            "patient_dfn": "patient_dfn",
            "lrdfn": "lrdfn",
            "parent_file": "parent_file",
            "last_specimen": "last_specimen",
            "institution": "institution",
        })
        print(f"  labs:           {n:>7,} rows  ({s} skipped)")

        # ── Lab chemistry results (from ^LR CH sub-nodes) ──
        lr_data = load_json("lab_results.json")
        patient_dfns = {r[0] for r in conn.execute(
            patients.select().with_only_columns(patients.c.dfn)
        ).fetchall()}
        lr_rows = []
        lr_skipped = 0
        for rec in lr_data:
            pt_dfn = safe_int(rec.get("patient_dfn"))
            if pt_dfn is None or pt_dfn not in patient_dfns:
                lr_skipped += 1
                continue
            lr_rows.append({
                "patient_dfn": pt_dfn,
                "lrdfn": safe_int(rec.get("lrdfn")),
                "collection_date": rec.get("collection_date"),
                "test_field": safe_int(rec.get("test_field")),
                "test_name": rec.get("test_name"),
                "result_value": rec.get("result_value"),
                "abnormal_flag": rec.get("abnormal_flag"),
                "units": rec.get("units"),
                "ref_low": rec.get("ref_low"),
                "ref_high": rec.get("ref_high"),
                "accession": rec.get("accession"),
            })
        for i in range(0, len(lr_rows), BATCH_SIZE):
            conn.execute(lab_results.insert(), lr_rows[i:i + BATCH_SIZE])
        print(f"  lab_results:    {len(lr_rows):>7,} rows  ({lr_skipped} skipped)")

        # ── New clinical tables ─────────────────────────────
        n, s = migrate_table(conn, appointments, "appointments.json", "ien", {
            "patient_dfn": "patient_dfn",
            "date": "date",
            "clinic_stop": "clinic_stop",
            "location": "location",
            "visit_entry": "visit_entry",
            "parent_encounter": "parent_encounter",
            "checkout": "checkout",
            "originating_process": "originating_process",
            "appointment_type": "appointment_type",
            "status": "status",
            "eligibility": "eligibility",
        })
        print(f"  appointments:   {n:>7,} rows  ({s} skipped)")

        n, s = migrate_table(conn, immunizations, "immunizations.json", "ien", {
            "patient_dfn": "patient_dfn",
            "immunization_type": "immunization_type",
            "visit": "visit",
            "series": "series",
            "lot": "lot",
            "reaction": "reaction",
        })
        print(f"  immunizations:  {n:>7,} rows  ({s} skipped)")

        n, s = migrate_table(conn, procedures, "procedures.json", "ien", {
            "patient_dfn": "patient_dfn",
            "cpt_code": "cpt_code",
            "visit": "visit",
            "provider_narrative": "provider_narrative",
            "diagnosis": "diagnosis",
        })
        print(f"  procedures:     {n:>7,} rows  ({s} skipped)")

        n, s = migrate_table(conn, visit_providers, "visit_providers.json", "ien", {
            "patient_dfn": "patient_dfn",
            "provider": "provider",
            "visit": "visit",
            "primary_secondary": "primary_secondary",
        })
        print(f"  visit_providers:{n:>7,} rows  ({s} skipped)")

        n, s = migrate_table(conn, visit_diagnoses, "visit_diagnoses.json", "ien", {
            "patient_dfn": "patient_dfn",
            "pov": "pov",
            "visit": "visit",
            "provider_narrative": "provider_narrative",
        })
        print(f"  visit_diagnoses:{n:>7,} rows  ({s} skipped)")

        n, s = migrate_table(conn, health_factors, "health_factors.json", "ien", {
            "patient_dfn": "patient_dfn",
            "health_factor_type": "health_factor_type",
            "visit": "visit",
            "level_severity": "level_severity",
        })
        print(f"  health_factors: {n:>7,} rows  ({s} skipped)")

        n, s = migrate_table(conn, adt_movements, "adt_movements.json", "ien", {
            "patient_dfn": "patient_dfn",
            "datetime": "datetime",
            "transaction": "transaction",
            "movement_type": "movement_type",
            "transfer_facility": "transfer_facility",
            "ward_location": "ward_location",
            "room_bed": "room_bed",
            "primary_physician": "primary_physician",
            "treating_specialty": "treating_specialty",
            "diagnosis_short": "diagnosis_short",
            "admission_movement": "admission_movement",
        })
        print(f"  adt_movements:  {n:>7,} rows  ({s} skipped)")

        n, s = migrate_table(conn, surgeries, "surgeries.json", "ien", {
            "patient_dfn": "patient_dfn",
            "procedure": "procedure",
            "major_minor": "major_minor",
            "surgery_specialty": "surgery_specialty",
            "preop_infection": "preop_infection",
            "date_of_operation": "date_of_operation",
            "schedule_type": "schedule_type",
            "admission_status": "admission_status",
        })
        print(f"  surgeries:      {n:>7,} rows  ({s} skipped)")

        n, s = migrate_table(conn, rad_reports, "rad_reports.json", "ien", {
            "patient_dfn": "patient_dfn",
            "day_case_number": "day_case_number",
            "exam_datetime": "exam_datetime",
            "case_number": "case_number",
            "report_status": "report_status",
            "date_entered": "date_entered",
            "verified_date": "verified_date",
            "reported_date": "reported_date",
        })
        print(f"  rad_reports:    {n:>7,} rows  ({s} skipped)")

        n, s = migrate_table(conn, exams, "exams.json", "ien", {
            "patient_dfn": "patient_dfn",
            "exam_type": "exam_type",
            "visit": "visit",
            "result": "result",
        })
        print(f"  exams:          {n:>7,} rows  ({s} skipped)")

        n, s = migrate_table(conn, patient_education, "patient_education.json", "ien", {
            "patient_dfn": "patient_dfn",
            "topic": "topic",
            "visit": "visit",
        })
        print(f"  pat_education:  {n:>7,} rows  ({s} skipped)")

        n, s = migrate_table(conn, skin_tests, "skin_tests.json", "ien", {
            "patient_dfn": "patient_dfn",
            "skin_test_type": "skin_test_type",
            "visit": "visit",
        })
        print(f"  skin_tests:     {n:>7,} rows  ({s} skipped)")

        total = conn.execute(text(
            "SELECT " + " + ".join(
                f"(SELECT COUNT(*) FROM {t})" for t in [
                    "patients", "problems", "allergies", "vitals",
                    "prescriptions", "orders", "notes", "consults", "labs",
                    "lab_results", "appointments", "immunizations",
                    "procedures", "visit_providers", "visit_diagnoses",
                    "health_factors", "adt_movements", "surgeries",
                    "rad_reports", "exams", "patient_education",
                    "skin_tests",
                ]
            )
        )).scalar()

    elapsed = time.time() - t0
    print(f"\nTotal: {total:,} rows in {elapsed:.1f}s")
    print("Migration complete.")


if __name__ == "__main__":
    main()
