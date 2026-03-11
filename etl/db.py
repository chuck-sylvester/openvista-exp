"""OpenVistA Database — PostgreSQL schema and connection."""
from __future__ import annotations

import os

from sqlalchemy import (
    Boolean, Column, Integer, MetaData, String, Table, Text,
    create_engine, text,
)

# Import 'settings' object from root-level config file
from config import settings

DATABASE_URL = settings.postgres.database_url

engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

metadata = MetaData()

patients = Table(
    "patients", metadata,
    Column("dfn", Integer, primary_key=True),
    Column("name", String(100), nullable=False),
    Column("sex", String(1)),
    Column("dob", String(20)),
    Column("ssn", String(12)),
    Column("street_1", String(100)),
    Column("street_2", String(100)),
    Column("city", String(50)),
    Column("state", String(30)),
    Column("zip", String(10)),
    Column("phone_home", String(30)),
    Column("phone_work", String(30)),
    Column("phone_cell", String(30)),
    Column("email", String(100)),
    Column("marital_status", String(20)),
    Column("religion", String(50)),
    Column("occupation", String(100)),
    Column("veteran", Boolean, default=False),
    Column("service_connected", Boolean, default=False),
    Column("sc_percentage", Integer),
    Column("date_entered", String(20)),
    Column("who_entered", String(100)),
)

problems = Table(
    "problems", metadata,
    Column("ifn", Integer, primary_key=True),
    Column("patient_dfn", Integer, nullable=False, index=True),
    Column("narrative_ptr", Text),
    Column("diagnosis_ptr", Text),
    Column("status", String(1)),
    Column("date_onset", String(20)),
    Column("date_entered", String(20)),
    Column("date_recorded", String(20)),
    Column("date_modified", String(20)),
    Column("date_resolved", String(20)),
    Column("priority", String(20)),
    Column("condition", String(20)),
    Column("responsible_provider", String(100)),
    Column("recording_provider", String(100)),
    Column("initial_provider", String(100)),
    Column("problem_number", Integer),
    Column("lexicon_term", String(100)),
    Column("clinic", String(100)),
    Column("service", String(100)),
    Column("facility", String(100)),
    Column("sc", Boolean),
    Column("ao", Boolean),
    Column("ir", Boolean),
    Column("ec", Boolean),
)

allergies = Table(
    "allergies", metadata,
    Column("ien", Integer, primary_key=True),
    Column("patient_dfn", Integer, nullable=False, index=True),
    Column("reactant", String(200)),
    Column("gmr_allergy_ptr", String(50)),
    Column("allergy_type", String(50)),
    Column("mechanism", String(50)),
    Column("origination_date", String(20)),
    Column("originator", String(100)),
    Column("verified", Boolean, default=False),
)

vitals = Table(
    "vitals", metadata,
    Column("ien", Integer, primary_key=True),
    Column("patient_dfn", Integer, nullable=False, index=True),
    Column("vital_type", String(50)),
    Column("rate", String(20)),
    Column("date_taken", String(30)),
    Column("date_entered", String(30)),
    Column("hospital_location", String(100)),
    Column("entered_by", String(100)),
)

prescriptions = Table(
    "prescriptions", metadata,
    Column("ien", Integer, primary_key=True),
    Column("patient_dfn", Integer, nullable=False, index=True),
    Column("drug", String(200)),
    Column("qty", String(20)),
    Column("days_supply", String(10)),
    Column("num_refills", String(10)),
    Column("refills_remaining", String(10)),
    Column("fill_date", String(20)),
    Column("status", String(20)),
    Column("provider", String(100)),
    Column("patient_status", String(50)),
    Column("sig_code", Text),
)

orders = Table(
    "orders", metadata,
    Column("ien", Integer, primary_key=True),
    Column("patient_dfn", Integer, nullable=False, index=True),
    Column("order_status", String(20)),
    Column("when_entered", String(30)),
    Column("start_date", String(30)),
    Column("stop_date", String(30)),
    Column("entered_by", String(100)),
    Column("current_location", String(100)),
    Column("nature_of_order", String(50)),
    Column("object_of_order", Text),
    Column("package_ref", String(50)),
    Column("current_agent", String(100)),
    Column("replacing_order", String(50)),
    Column("date_released", String(30)),
    Column("elapse_event", String(50)),
)

notes = Table(
    "notes", metadata,
    Column("ien", Integer, primary_key=True),
    Column("patient_dfn", Integer, nullable=False, index=True),
    Column("document_type", String(200)),
    Column("status", String(10)),
    Column("episode_date", String(30)),
    Column("entry_date", String(30)),
    Column("author", String(100)),
    Column("expected_signer", String(100)),
    Column("attending", String(100)),
    Column("signed_by", String(100)),
    Column("signature_date", String(30)),
    Column("signature_status", String(20)),
    Column("hospital_location", String(100)),
    Column("visit", String(50)),
    Column("parent_document", String(50)),
    Column("body", Text),
)

consults = Table(
    "consults", metadata,
    Column("ien", Integer, primary_key=True),
    Column("patient_dfn", Integer, index=True),
    Column("date_entered", String(30)),
    Column("order_ref", String(50)),
    Column("patient_location", String(100)),
    Column("to_service", String(100)),
    Column("from_location", String(100)),
    Column("date_requested", String(30)),
    Column("procedure_type", String(50)),
    Column("urgency", String(50)),
    Column("place_of_consultation", String(100)),
    Column("attention", String(100)),
    Column("cprs_status", String(50)),
    Column("last_action", String(50)),
    Column("sending_provider", String(100)),
    Column("result", String(200)),
    Column("mode_of_entry", String(20)),
)

labs = Table(
    "labs", metadata,
    Column("ien", Integer, primary_key=True),
    Column("patient_dfn", Integer, index=True),
    Column("lrdfn", String(20)),
    Column("parent_file", String(50)),
    Column("last_specimen", String(50)),
    Column("institution", String(100)),
)

lab_results = Table(
    "lab_results", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("patient_dfn", Integer, nullable=False, index=True),
    Column("lrdfn", Integer),
    Column("collection_date", String(30)),
    Column("test_field", Integer),
    Column("test_name", String(200)),
    Column("result_value", String(50)),
    Column("abnormal_flag", String(10)),
    Column("units", String(50)),
    Column("ref_low", String(20)),
    Column("ref_high", String(20)),
    Column("accession", String(50)),
)

# ── New clinical tables ───────────────────────────────────────

appointments = Table(
    "appointments", metadata,
    Column("ien", Integer, primary_key=True),
    Column("patient_dfn", Integer, nullable=False, index=True),
    Column("date", String(30)),
    Column("clinic_stop", String(100)),
    Column("location", String(200)),
    Column("visit_entry", String(50)),
    Column("parent_encounter", String(50)),
    Column("checkout", String(30)),
    Column("originating_process", String(50)),
    Column("appointment_type", String(100)),
    Column("status", String(50)),
    Column("eligibility", String(50)),
)

immunizations = Table(
    "immunizations", metadata,
    Column("ien", Integer, primary_key=True),
    Column("patient_dfn", Integer, nullable=False, index=True),
    Column("immunization_type", String(200)),
    Column("visit", String(50)),
    Column("series", String(50)),
    Column("lot", String(100)),
    Column("reaction", String(200)),
)

procedures = Table(
    "procedures", metadata,
    Column("ien", Integer, primary_key=True),
    Column("patient_dfn", Integer, nullable=False, index=True),
    Column("cpt_code", String(200)),
    Column("visit", String(50)),
    Column("provider_narrative", String(200)),
    Column("diagnosis", String(200)),
)

visit_providers = Table(
    "visit_providers", metadata,
    Column("ien", Integer, primary_key=True),
    Column("patient_dfn", Integer, nullable=False, index=True),
    Column("provider", String(200)),
    Column("visit", String(50)),
    Column("primary_secondary", String(20)),
)

visit_diagnoses = Table(
    "visit_diagnoses", metadata,
    Column("ien", Integer, primary_key=True),
    Column("patient_dfn", Integer, nullable=False, index=True),
    Column("pov", String(200)),
    Column("visit", String(50)),
    Column("provider_narrative", String(200)),
)

health_factors = Table(
    "health_factors", metadata,
    Column("ien", Integer, primary_key=True),
    Column("patient_dfn", Integer, nullable=False, index=True),
    Column("health_factor_type", String(200)),
    Column("visit", String(50)),
    Column("level_severity", String(50)),
)

adt_movements = Table(
    "adt_movements", metadata,
    Column("ien", Integer, primary_key=True),
    Column("patient_dfn", Integer, nullable=False, index=True),
    Column("datetime", String(30)),
    Column("transaction", String(100)),
    Column("movement_type", String(200)),
    Column("transfer_facility", String(200)),
    Column("ward_location", String(200)),
    Column("room_bed", String(50)),
    Column("primary_physician", String(200)),
    Column("treating_specialty", String(200)),
    Column("diagnosis_short", String(200)),
    Column("admission_movement", String(50)),
)

surgeries = Table(
    "surgeries", metadata,
    Column("ien", Integer, primary_key=True),
    Column("patient_dfn", Integer, nullable=False, index=True),
    Column("procedure", String(200)),
    Column("major_minor", String(10)),
    Column("surgery_specialty", String(200)),
    Column("preop_infection", String(50)),
    Column("date_of_operation", String(30)),
    Column("schedule_type", String(50)),
    Column("admission_status", String(20)),
)

rad_reports = Table(
    "rad_reports", metadata,
    Column("ien", Integer, primary_key=True),
    Column("patient_dfn", Integer, nullable=False, index=True),
    Column("day_case_number", String(30)),
    Column("exam_datetime", String(30)),
    Column("case_number", String(20)),
    Column("report_status", String(30)),
    Column("date_entered", String(30)),
    Column("verified_date", String(30)),
    Column("reported_date", String(30)),
)

exams = Table(
    "exams", metadata,
    Column("ien", Integer, primary_key=True),
    Column("patient_dfn", Integer, nullable=False, index=True),
    Column("exam_type", String(200)),
    Column("visit", String(50)),
    Column("result", String(200)),
)

patient_education = Table(
    "patient_education", metadata,
    Column("ien", Integer, primary_key=True),
    Column("patient_dfn", Integer, nullable=False, index=True),
    Column("topic", String(200)),
    Column("visit", String(50)),
)

skin_tests = Table(
    "skin_tests", metadata,
    Column("ien", Integer, primary_key=True),
    Column("patient_dfn", Integer, nullable=False, index=True),
    Column("skin_test_type", String(200)),
    Column("visit", String(50)),
)


def create_tables():
    metadata.create_all(engine)


def drop_tables():
    metadata.drop_all(engine)
