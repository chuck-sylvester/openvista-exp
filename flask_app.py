"""OpenVistA — Modern Healthcare Application
VistA (3.7M LOC MUMPS, 1966-present) modernized.
Real data from VistA VEHU via direct MUMPS extraction, served from PostgreSQL.
Live MUMPS globals access via docker exec into vista-vehu container.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from flask import Flask, request, jsonify, send_file
from sqlalchemy import func, select, text

from db import (
    adt_movements, allergies, appointments, consults, engine, exams,
    health_factors, immunizations, lab_results, labs, notes, orders,
    patient_education, patients, prescriptions, problems, procedures,
    rad_reports, skin_tests, surgeries, visit_diagnoses, visit_providers,
    vitals,
)

BASE = Path(__file__).parent

PACKAGES = [
    "Patient Registration", "Problem List", "Vitals",
    "Allergy / Adverse Reaction", "Outpatient Pharmacy", "Lab Service",
    "Order Entry (CPOE)", "Consult Request Tracking", "Mental Health",
    "Radiology", "Inpatient Medications", "PCE Patient Care Encounter",
    "TIU Clinical Notes", "Health Summary", "Scheduling",
]

TIU_STATUS = {
    "5": "UNSIGNED", "6": "UNCOSIGNED", "7": "COMPLETED",
    "8": "AMENDED", "13": "DELETED", "14": "RETRACTED", "15": "PURGED",
}

ORDER_STATUS = {
    "0": "DISCONTINUED", "1": "COMPLETE", "2": "FLAGGED",
    "3": "HELD", "5": "PENDING", "6": "ACTIVE", "7": "EXPIRED",
    "8": "SCHEDULED", "9": "PARTIAL RESULTS", "10": "DELAYED",
    "11": "UNRELEASED", "12": "DISCONTINUED/EDIT", "13": "CANCELLED",
    "14": "LAPSED", "15": "RENEWED", "18": "DISCONTINUED",
}

APPT_STATUS = {
    "2": "CHECKED OUT", "8": "INPATIENT", "12": "NO SHOW", "14": "CHECKED IN",
}

RX_STATUS = {
    "0": "ACTIVE", "1": "NON-VERIFIED", "4": "HOLD",
    "5": "SUSPENDED", "11": "EXPIRED", "12": "DISCONTINUED",
    "13": "DELETED", "14": "DISCONTINUED (EDIT)",
    "15": "DISCONTINUED BY PROVIDER",
}

app = Flask(__name__, static_folder=None)


# ── Helpers ──────────────────────────────────────────────────────

def _mask_ssn(ssn: str | None) -> str:
    if not ssn or len(ssn) < 4:
        return "***-**-****"
    return f"***-**-{ssn[-4:]}"


def _row_to_dict(row) -> dict:
    return dict(row._mapping)


def _patient_summary(row) -> dict:
    p = _row_to_dict(row) if not isinstance(row, dict) else row
    return {
        "dfn": str(p["dfn"]),
        "name": p.get("name", ""),
        "sex": p.get("sex", ""),
        "dob": p.get("dob", ""),
        "ssn": _mask_ssn(p.get("ssn")),
        "city": p.get("city", ""),
        "state": p.get("state", ""),
        "veteran": p.get("veteran", False),
        "service_connected": p.get("service_connected", False),
        "sc_percentage": p.get("sc_percentage"),
        "phone_home": p.get("phone_home", ""),
        "phone_work": p.get("phone_work", ""),
        "phone_cell": p.get("phone_cell", ""),
        "email": p.get("email", ""),
        "occupation": p.get("occupation", ""),
        "street_1": p.get("street_1", ""),
        "zip": p.get("zip", ""),
    }


# ── Routes ───────────────────────────────────────────────────────

@app.route("/")
def landing():
    return send_file(BASE / "landing.html")


@app.route("/app")
def clinical_app():
    resp = send_file(BASE / "index.html")
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return resp


@app.route("/api/overview")
def overview():
    with engine.connect() as conn:
        counts = {}
        for name, table in [
            ("patients", patients), ("problems", problems),
            ("allergies", allergies), ("vitals", vitals),
            ("prescriptions", prescriptions), ("orders", orders),
            ("notes", notes), ("consults", consults), ("labs", labs),
            ("appointments", appointments), ("immunizations", immunizations),
            ("procedures", procedures), ("visit_providers", visit_providers),
            ("visit_diagnoses", visit_diagnoses),
            ("health_factors", health_factors),
            ("adt_movements", adt_movements), ("surgeries", surgeries),
            ("rad_reports", rad_reports), ("exams", exams),
            ("patient_education", patient_education),
            ("skin_tests", skin_tests), ("lab_results", lab_results),
        ]:
            counts[name] = conn.execute(select(func.count()).select_from(table)).scalar()
    return jsonify({
        "system": "OpenVistA",
        "source": "VistA VEHU — real MUMPS globals",
        "packages": len(PACKAGES),
        "package_list": PACKAGES,
        "data": counts,
        "total_records": sum(counts.values()),
    })


@app.route("/api/patients")
def patients_list():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    search = request.args.get("search", "").upper()

    with engine.connect() as conn:
        base = select(patients)
        if search:
            base = base.where(patients.c.name.ilike(f"%{search}%"))

        total = conn.execute(
            select(func.count()).select_from(base.subquery())
        ).scalar()

        rows = conn.execute(
            base.order_by(patients.c.dfn)
            .limit(per_page)
            .offset((page - 1) * per_page)
        ).fetchall()

    return jsonify({
        "patients": [_patient_summary(r) for r in rows],
        "pagination": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page if total else 0,
        },
    })


@app.route("/api/patient/<dfn>")
def patient_detail(dfn: str):
    with engine.connect() as conn:
        row = conn.execute(
            select(patients).where(patients.c.dfn == int(dfn))
        ).fetchone()
        if not row:
            return jsonify({"error": "Patient not found"}), 404
        summary = _patient_summary(row)
        dfn_int = int(dfn)
        summary["problems_count"] = conn.execute(
            select(func.count()).where(problems.c.patient_dfn == dfn_int)
        ).scalar()
        summary["allergies_count"] = conn.execute(
            select(func.count()).where(allergies.c.patient_dfn == dfn_int)
        ).scalar()
        summary["vitals_count"] = conn.execute(
            select(func.count()).where(vitals.c.patient_dfn == dfn_int)
        ).scalar()
        summary["rx_count"] = conn.execute(
            select(func.count()).where(prescriptions.c.patient_dfn == dfn_int)
        ).scalar()
        summary["orders_count"] = conn.execute(
            select(func.count()).where(orders.c.patient_dfn == dfn_int)
        ).scalar()
        summary["notes_count"] = conn.execute(
            select(func.count()).where(notes.c.patient_dfn == dfn_int)
        ).scalar()
        summary["appointments_count"] = conn.execute(
            select(func.count()).where(appointments.c.patient_dfn == dfn_int)
        ).scalar()
        summary["immunizations_count"] = conn.execute(
            select(func.count()).where(immunizations.c.patient_dfn == dfn_int)
        ).scalar()
        summary["surgeries_count"] = conn.execute(
            select(func.count()).where(surgeries.c.patient_dfn == dfn_int)
        ).scalar()
        summary["consults_count"] = conn.execute(
            select(func.count()).where(consults.c.patient_dfn == dfn_int)
        ).scalar()
        summary["labs_count"] = conn.execute(
            select(func.count()).where(lab_results.c.patient_dfn == dfn_int)
        ).scalar()
    return jsonify(summary)


@app.route("/api/patient/<dfn>/problems")
def patient_problems(dfn: str):
    with engine.connect() as conn:
        rows = conn.execute(
            select(problems).where(problems.c.patient_dfn == int(dfn))
        ).fetchall()
    return jsonify({"problems": [{
        "id": r.ifn,
        "narrative": r.narrative_ptr or "",
        "diagnosis": r.diagnosis_ptr or "",
        "status": r.status or "",
        "date_onset": r.date_onset or "",
        "date_entered": r.date_entered or "",
        "date_resolved": r.date_resolved or "",
        "date_modified": r.date_modified or "",
        "priority": r.priority or "",
        "provider": r.responsible_provider or "",
        "condition": r.condition or "",
        "sc": r.sc,
    } for r in rows]})


@app.route("/api/patient/<dfn>/allergies")
def patient_allergies(dfn: str):
    with engine.connect() as conn:
        rows = conn.execute(
            select(allergies).where(allergies.c.patient_dfn == int(dfn))
        ).fetchall()
    return jsonify({"allergies": [{
        "id": r.ien,
        "reactant": r.reactant or "",
        "allergy_type": r.allergy_type or "",
        "entry_date": r.origination_date or "",
        "mechanism": r.mechanism or "",
        "verified": r.verified,
    } for r in rows]})


@app.route("/api/patient/<dfn>/vitals")
def patient_vitals(dfn: str):
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 100, type=int)
    dfn_int = int(dfn)

    with engine.connect() as conn:
        total = conn.execute(
            select(func.count()).where(vitals.c.patient_dfn == dfn_int)
        ).scalar()
        rows = conn.execute(
            select(vitals)
            .where(vitals.c.patient_dfn == dfn_int)
            .order_by(vitals.c.date_taken.desc())
            .limit(per_page)
            .offset((page - 1) * per_page)
        ).fetchall()

    return jsonify({
        "vitals": [{
            "id": v.ien,
            "vital_name": v.vital_type or "",
            "reading": v.rate or "",
            "datetime_taken": v.date_taken or "",
            "location": v.hospital_location or "",
            "entered_by": v.entered_by or "",
        } for v in rows],
        "pagination": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page if total else 0,
        },
    })


@app.route("/api/patient/<dfn>/prescriptions")
def patient_prescriptions(dfn: str):
    with engine.connect() as conn:
        rows = conn.execute(
            select(prescriptions)
            .where(prescriptions.c.patient_dfn == int(dfn))
            .where(prescriptions.c.drug.isnot(None))
            .where(prescriptions.c.drug != "")
        ).fetchall()
    return jsonify({"prescriptions": [{
        "id": r.ien,
        "drug_name": r.drug or "",
        "qty": r.qty or "",
        "days_supply": r.days_supply or "",
        "refills_remaining": r.num_refills or "",
        "issue_date": r.fill_date or "",
        "status": RX_STATUS.get(str(r.status or ""), r.status or ""),
        "provider": r.provider or "",
    } for r in rows]})


@app.route("/api/patient/<dfn>/orders")
def patient_orders(dfn: str):
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    dfn_int = int(dfn)

    with engine.connect() as conn:
        total = conn.execute(
            select(func.count()).where(orders.c.patient_dfn == dfn_int)
        ).scalar()
        rows = conn.execute(
            select(orders)
            .where(orders.c.patient_dfn == dfn_int)
            .order_by(orders.c.when_entered.desc())
            .limit(per_page)
            .offset((page - 1) * per_page)
        ).fetchall()

    return jsonify({
        "orders": [{
            "id": o.ien,
            "status_name": ORDER_STATUS.get(str(o.order_status or ""), o.order_status or ""),
            "when_entered": o.when_entered or "",
            "start_datetime": o.start_date or "",
            "stop_date": o.stop_date or "",
            "provider": o.entered_by or "",
            "location": o.current_location or "",
        } for o in rows],
        "pagination": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page if total else 0,
        },
    })


@app.route("/api/patient/<dfn>/notes")
def patient_notes(dfn: str):
    with engine.connect() as conn:
        rows = conn.execute(
            select(notes).where(notes.c.patient_dfn == int(dfn))
        ).fetchall()
    return jsonify({"notes": [{
        "id": n.ien,
        "title": n.document_type or "",
        "document_type": n.document_type or "",
        "status_name": TIU_STATUS.get(str(n.status or ""), n.status or ""),
        "document_date": n.episode_date or "",
        "author": n.author or "",
        "signature_status": n.signature_status or "",
        "entry_date": n.entry_date or "",
        "attending": n.attending or "",
        "body": n.body or "",
    } for n in rows]})


@app.route("/api/patient/<dfn>/consults")
def patient_consults(dfn: str):
    with engine.connect() as conn:
        rows = conn.execute(
            select(consults).where(consults.c.patient_dfn == int(dfn))
        ).fetchall()
    return jsonify({"consults": [{
        "id": c.ien,
        "service": c.to_service or "",
        "date_of_request": c.date_requested or "",
        "urgency": c.urgency or "",
        "status_name": c.cprs_status or "",
        "from_location": c.from_location or "",
        "disposition": c.result or "",
        "sending_provider": c.sending_provider or "",
    } for c in rows]})


@app.route("/api/patient/<dfn>/labs")
def patient_labs(dfn: str):
    with engine.connect() as conn:
        rows = conn.execute(
            select(lab_results)
            .where(lab_results.c.patient_dfn == int(dfn))
            .order_by(lab_results.c.collection_date.desc())
        ).fetchall()
    return jsonify({"labs": [{
        "id": r.id,
        "collection_datetime": r.collection_date or "",
        "test_name": r.test_name or "",
        "result_value": r.result_value or "",
        "units": r.units or "",
        "reference_range": f"{r.ref_low}-{r.ref_high}" if r.ref_low and r.ref_high else "",
        "abnormal_flag": r.abnormal_flag or "",
    } for r in rows]})


@app.route("/api/patient/<dfn>/appointments")
def patient_appointments(dfn: str):
    with engine.connect() as conn:
        rows = conn.execute(
            select(appointments)
            .where(appointments.c.patient_dfn == int(dfn))
            .order_by(appointments.c.date.desc())
        ).fetchall()
    return jsonify({"appointments": [{
        "id": r.ien,
        "appointment_datetime": r.date or "",
        "clinic_name": r.location or "",
        "clinic_stop": r.clinic_stop or "",
        "status": APPT_STATUS.get(str(r.status or ""), r.status or ""),
        "checkout": r.checkout or "",
        "appointment_type": r.appointment_type or "",
        "eligibility": r.eligibility or "",
    } for r in rows]})


@app.route("/api/patient/<dfn>/mh")
def patient_mh(dfn: str):
    with engine.connect() as conn:
        rows = conn.execute(
            select(health_factors).where(health_factors.c.patient_dfn == int(dfn))
        ).fetchall()
    return jsonify({"results": [{
        "id": r.ien,
        "instrument": r.health_factor_type or "",
        "date_given": "",
        "total_score": r.level_severity or "",
        "interpretation": "",
    } for r in rows]})


@app.route("/api/patient/<dfn>/immunizations")
def patient_immunizations(dfn: str):
    with engine.connect() as conn:
        rows = conn.execute(
            select(immunizations).where(immunizations.c.patient_dfn == int(dfn))
        ).fetchall()
    return jsonify({"immunizations": [{
        "id": r.ien,
        "immunization": r.immunization_type or "",
        "series": r.series or "",
        "reaction": r.reaction or "",
        "visit": r.visit or "",
    } for r in rows]})


@app.route("/api/patient/<dfn>/surgeries")
def patient_surgeries(dfn: str):
    with engine.connect() as conn:
        rows = conn.execute(
            select(surgeries).where(surgeries.c.patient_dfn == int(dfn))
        ).fetchall()
    return jsonify({"surgeries": [{
        "id": r.ien,
        "procedure": r.procedure or "",
        "major_minor": r.major_minor or "",
        "specialty": r.surgery_specialty or "",
        "date_of_operation": r.date_of_operation or "",
        "schedule_type": r.schedule_type or "",
        "admission_status": r.admission_status or "",
    } for r in rows]})


@app.route("/api/patient/<dfn>/procedures")
def patient_procedures(dfn: str):
    with engine.connect() as conn:
        rows = conn.execute(
            select(procedures).where(procedures.c.patient_dfn == int(dfn))
        ).fetchall()
    return jsonify({"procedures": [{
        "id": r.ien,
        "cpt_code": r.cpt_code or "",
        "provider_narrative": r.provider_narrative or "",
        "visit": r.visit or "",
    } for r in rows]})


@app.route("/api/patient/<dfn>/adt")
def patient_adt(dfn: str):
    with engine.connect() as conn:
        rows = conn.execute(
            select(adt_movements)
            .where(adt_movements.c.patient_dfn == int(dfn))
            .order_by(adt_movements.c.datetime.desc())
        ).fetchall()
    return jsonify({"movements": [{
        "id": r.ien,
        "datetime": r.datetime or "",
        "movement_type": r.movement_type or "",
        "ward": r.ward_location or "",
        "room_bed": r.room_bed or "",
        "physician": r.primary_physician or "",
        "diagnosis": r.diagnosis_short or "",
    } for r in rows]})


@app.route("/api/patient/<dfn>/rad_reports")
def patient_rad_reports(dfn: str):
    with engine.connect() as conn:
        rows = conn.execute(
            select(rad_reports).where(rad_reports.c.patient_dfn == int(dfn))
        ).fetchall()
    return jsonify({"rad_reports": [{
        "id": r.ien,
        "day_case": r.day_case_number or "",
        "exam_date": r.exam_datetime or "",
        "status": r.report_status or "",
        "verified_date": r.verified_date or "",
    } for r in rows]})


@app.route("/api/patient/<dfn>/timeline")
def patient_timeline(dfn: str):
    events = []
    dfn_int = int(dfn)
    with engine.connect() as conn:
        for r in conn.execute(select(problems).where(problems.c.patient_dfn == dfn_int)):
            events.append({"date": r.date_onset or "", "type": "problem",
                           "title": r.narrative_ptr or "", "detail": f"Status: {'Active' if r.status == 'A' else 'Inactive'}"})

        for r in conn.execute(select(prescriptions).where(prescriptions.c.patient_dfn == dfn_int)
                              .where(prescriptions.c.drug.isnot(None))):
            events.append({"date": r.fill_date or "", "type": "rx",
                           "title": r.drug or "", "detail": f"Qty: {r.qty or ''}, Days: {r.days_supply or ''}"})

        for r in conn.execute(select(lab_results).where(lab_results.c.patient_dfn == dfn_int)):
            events.append({"date": r.collection_date or "", "type": "lab",
                           "title": r.test_name or "", "detail": f"{r.result_value or ''} {r.units or ''}"})

        for r in conn.execute(select(appointments).where(appointments.c.patient_dfn == dfn_int)):
            events.append({"date": r.date or "", "type": "appointment",
                           "title": r.location or "", "detail": APPT_STATUS.get(str(r.status or ""), r.status or "")})

        for r in conn.execute(select(notes).where(notes.c.patient_dfn == dfn_int)):
            events.append({"date": r.episode_date or "", "type": "note",
                           "title": r.document_type or "", "detail": TIU_STATUS.get(str(r.status or ""), r.status or "")})

        for r in conn.execute(select(orders).where(orders.c.patient_dfn == dfn_int)
                              .order_by(orders.c.when_entered.desc()).limit(50)):
            events.append({"date": r.when_entered or "", "type": "order",
                           "title": ORDER_STATUS.get(str(r.order_status or ""), r.order_status or ""),
                           "detail": r.current_location or ""})

        for r in conn.execute(select(surgeries).where(surgeries.c.patient_dfn == dfn_int)):
            events.append({"date": r.date_of_operation or "", "type": "surgery",
                           "title": "Surgery", "detail": r.surgery_specialty or ""})

        for r in conn.execute(select(adt_movements).where(adt_movements.c.patient_dfn == dfn_int)):
            events.append({"date": r.datetime or "", "type": "adt",
                           "title": r.ward_location or "Transfer", "detail": r.diagnosis_short or ""})

        for r in conn.execute(select(immunizations).where(immunizations.c.patient_dfn == dfn_int)):
            events.append({"date": "", "type": "immunization",
                           "title": r.immunization_type or "", "detail": r.series or ""})

        for r in conn.execute(select(rad_reports).where(rad_reports.c.patient_dfn == dfn_int)):
            events.append({"date": r.exam_datetime or "", "type": "radiology",
                           "title": "Radiology", "detail": f"Case #{r.day_case_number or ''}"})

    for e in events:
        raw = (e["date"] or "")[:10]
        e["sort_date"] = raw if len(raw) == 10 and raw[4:5] == "-" else ""

    events.sort(key=lambda e: e["sort_date"], reverse=True)
    return jsonify({"events": events[:500]})


# ── MUMPS Live Access ────────────────────────────────────────────

MUMPS_CONTAINER = "vista-vehu"
_RE_NUMERIC = re.compile(r"^\d+$")

ALLOWED_GLOBALS = {
    "^DPT", "^AUPNPROB", "^GMR(120.8)", "^GMR(120.5)", "^PSRX",
    "^OR(100)", "^TIU(8925)", "^GMR(123)", "^LR", "^SRF", "^SCE",
    "^AUPNVIMM", "^AUPNVCPT", "^AUPNVPRV", "^AUPNVPOV", "^AUPNVHF",
    "^AUPNVXAM", "^AUPNVPED", "^AUPNVSK", "^DGPM", "^RARPT",
    "^PSDRUG", "^VA(200)", "^DIC", "^DD", "^LAB(60)", "^ICD9",
    "^SRO(137.45)", "^AUTNPOV",
}

TAB_GLOBAL_MAP = {
    "problems":      {"global": "^AUPNPROB",   "ref": "^AUPNPROB(",    "table": problems,      "ien_col": "ifn"},
    "allergies":     {"global": "^GMR(120.8)",  "ref": "^GMR(120.8,",   "table": allergies,     "ien_col": "ien"},
    "vitals":        {"global": "^GMR(120.5)",  "ref": "^GMR(120.5,",   "table": vitals,        "ien_col": "ien"},
    "meds":          {"global": "^PSRX",        "ref": "^PSRX(",        "table": prescriptions, "ien_col": "ien"},
    "orders":        {"global": "^OR(100)",     "ref": "^OR(100,",      "table": orders,        "ien_col": "ien"},
    "notes":         {"global": "^TIU(8925)",   "ref": "^TIU(8925,",    "table": notes,         "ien_col": "ien"},
    "consults":      {"global": "^GMR(123)",    "ref": "^GMR(123,",     "table": consults,      "ien_col": "ien"},
    "surgeries":     {"global": "^SRF",         "ref": "^SRF(",         "table": surgeries,     "ien_col": "ien"},
    "schedule":      {"global": "^SCE",         "ref": "^SCE(",         "table": appointments,  "ien_col": "ien"},
    "immunizations": {"global": "^AUPNVIMM",   "ref": "^AUPNVIMM(",   "table": immunizations, "ien_col": "ien"},
    "procedures":    {"global": "^AUPNVCPT",   "ref": "^AUPNVCPT(",   "table": procedures,    "ien_col": "ien"},
    "radiology":     {"global": "^RARPT",       "ref": "^RARPT(",       "table": rad_reports,   "ien_col": "ien"},
}


def _run_mumps(cmd: str, timeout: int = 10) -> str:
    try:
        result = subprocess.run(
            ["docker", "exec", "-i", MUMPS_CONTAINER,
             "su", "-", "vehu", "-c", "yottadb -dir"],
            input=cmd + "\nH\n",
            capture_output=True, text=True, timeout=timeout,
        )
        lines = result.stdout.strip().split("\n")
        return "\n".join(
            l for l in lines if not l.startswith("VEHU>") and l.strip()
        )
    except subprocess.TimeoutExpired:
        return ""
    except FileNotFoundError:
        return ""


def _validate_global(global_name: str) -> bool:
    return global_name in ALLOWED_GLOBALS


def _validate_ien(ien: str) -> bool:
    return bool(_RE_NUMERIC.match(ien))


def _explore_global(global_ref: str, ien: str, max_nodes: int = 100) -> dict:
    """Read all first-level sub-nodes of a global entry."""
    base = f"{global_ref}{ien},"
    cmd = (
        f'S I="",C=0 '
        f'F  S I=$O({base}I)) Q:I=""  '
        f'S C=C+1 Q:C>{max_nodes}  '
        f'W "N:",I,"=:",$G({base}I)),!'
    )
    output = _run_mumps(cmd)
    nodes = {}
    for line in output.split("\n"):
        if line.startswith("N:"):
            eq = line.find("=:", 2)
            if eq > 2:
                nodes[line[2:eq]] = line[eq + 2:]
    return nodes


@app.route("/api/mumps/explore")
def mumps_explore():
    """Explore sub-nodes of a MUMPS global entry."""
    global_name = request.args.get("global", "")
    ien = request.args.get("ien", "")
    if not global_name or not ien:
        return jsonify({"error": "global and ien required"}), 400
    if not _validate_global(global_name):
        return jsonify({"error": f"Global {global_name} not allowed"}), 403
    if not _validate_ien(ien):
        return jsonify({"error": "IEN must be numeric"}), 400

    ref = global_name + "(" if "(" not in global_name else global_name + ","
    if global_name.endswith(")"):
        ref = global_name[:-1] + ","

    nodes = _explore_global(ref, ien)
    top_val = _run_mumps(f'W $G({ref}{ien}))')
    return jsonify({
        "global": global_name,
        "ien": ien,
        "top_value": top_val.strip(),
        "nodes": nodes,
    })


@app.route("/api/mumps/patient/<dfn>/globals/<tab>")
def mumps_patient_globals(dfn: str, tab: str):
    """Get MUMPS globals for a patient's clinical tab records."""
    if tab not in TAB_GLOBAL_MAP:
        return jsonify({"error": f"Unknown tab: {tab}"}), 400
    if not _validate_ien(dfn):
        return jsonify({"error": "DFN must be numeric"}), 400

    cfg = TAB_GLOBAL_MAP[tab]
    table = cfg["table"]
    ien_col_name = cfg["ien_col"]
    ien_col = getattr(table.c, ien_col_name)

    with engine.connect() as conn:
        rows = conn.execute(
            select(ien_col)
            .where(table.c.patient_dfn == int(dfn))
            .limit(30)
        ).fetchall()
    iens = [str(r[0]) for r in rows if r[0]]

    if not iens:
        return jsonify({
            "tab": tab,
            "global": cfg["global"],
            "records": [],
        })

    ref = cfg["ref"]
    batch_parts = []
    for i_ien in iens[:20]:
        batch_parts.append(
            f'W "REC:{i_ien}=:",$G({ref}{i_ien},0)),!'
        )
    cmd = " ".join(batch_parts)
    output = _run_mumps(cmd, timeout=15)

    records = []
    for line in output.split("\n"):
        if line.startswith("REC:"):
            eq = line.find("=:", 4)
            if eq > 4:
                rec_ien = line[4:eq]
                rec_val = line[eq + 2:]
                records.append({
                    "ien": rec_ien,
                    "global_ref": f"{ref}{rec_ien})",
                    "node_0": rec_val,
                })

    return jsonify({
        "tab": tab,
        "global": cfg["global"],
        "records": records,
        "total_iens": len(iens),
    })


@app.route("/api/mumps/read")
def mumps_read():
    """Read a single MUMPS global reference."""
    ref = request.args.get("ref", "")
    if not ref:
        return jsonify({"error": "ref parameter required"}), 400
    global_match = re.match(r"\^[A-Z]+(\([0-9.,]+\))?", ref)
    if not global_match:
        return jsonify({"error": "Invalid global reference"}), 400
    global_base = ref.split("(")[0] if "(" in ref else ref
    extra = ref[len(global_base):]
    if "(" in extra:
        full_global = global_base + "(" + extra.split("(", 1)[1]
    else:
        full_global = global_base
    if not _validate_global(global_base) and not _validate_global(full_global.split(",")[0].rstrip(")")):
        return jsonify({"error": f"Global not allowed"}), 403
    value = _run_mumps(f'W $G({ref})')
    return jsonify({"ref": ref, "value": value.strip()})


@app.route("/api/mumps/write", methods=["POST"])
def mumps_write():
    """Write a value to a MUMPS global (piece-level)."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    global_name = data.get("global", "")
    ien = str(data.get("ien", ""))
    node = str(data.get("node", "0"))
    piece = data.get("piece")
    value = data.get("value", "")

    if not global_name or not ien:
        return jsonify({"error": "global and ien required"}), 400
    if not _validate_global(global_name):
        return jsonify({"error": f"Global {global_name} not allowed"}), 403
    if not _validate_ien(ien):
        return jsonify({"error": "IEN must be numeric"}), 400
    if piece is not None and not isinstance(piece, int):
        return jsonify({"error": "piece must be an integer"}), 400

    safe_val = str(value).replace('"', '""')
    ref = global_name + "(" if "(" not in global_name else global_name + ","
    if global_name.endswith(")"):
        ref = global_name[:-1] + ","
    full_ref = f"{ref}{ien},{node})"

    before = _run_mumps(f'W $G({full_ref})')

    if piece is not None:
        cmd = f'S $P({full_ref},"^",{piece})="{safe_val}"'
    else:
        cmd = f'S {full_ref}="{safe_val}"'
    _run_mumps(cmd)

    after = _run_mumps(f'W $G({full_ref})')

    return jsonify({
        "global": global_name,
        "ien": ien,
        "node": node,
        "piece": piece,
        "ref": full_ref,
        "before": before.strip(),
        "after": after.strip(),
        "value_written": value,
    })


@app.route("/api/mumps/status")
def mumps_status():
    """Check if MUMPS container is accessible."""
    version = _run_mumps('W $ZV')
    if version.strip():
        return jsonify({"status": "online", "version": version.strip()})
    return jsonify({"status": "offline", "version": ""}), 503


# ── Clinical Write Operations ────────────────────────────────────

from datetime import datetime

VITAL_TYPES = {
    "TEMPERATURE": "2", "BLOOD PRESSURE": "1", "PULSE": "5",
    "RESPIRATION": "3", "HEIGHT": "8", "WEIGHT": "9",
    "PAIN": "22", "PULSE OXIMETRY": "21",
}


def _next_ien(global_ref: str) -> str:
    """Get next available IEN for a global using reverse $ORDER from a high numeric seed."""
    out = _run_mumps(f'W $O({global_ref}999999999),-1)')
    try:
        return str(int(out.strip()) + 1)
    except (ValueError, TypeError):
        return "1"


def _fm_date_now() -> str:
    """Current date/time in FileMan format: 3YYMMDD.HHMMSS"""
    now = datetime.now()
    yr = now.year - 1700
    return f"{yr}{now.month:02d}{now.day:02d}.{now.hour:02d}{now.minute:02d}{now.second:02d}"


def _iso_to_fm(date_str: str) -> str:
    """Convert ISO date (YYYY-MM-DD) to FileMan date (3YYMMDD)."""
    if not date_str:
        return _fm_date_now().split(".")[0]
    try:
        dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
        yr = dt.year - 1700
        return f"{yr}{dt.month:02d}{dt.day:02d}"
    except ValueError:
        return _fm_date_now().split(".")[0]


def _lookup_ien(global_name: str, search_name: str) -> str | None:
    """Reverse lookup: find IEN by name in a lookup global."""
    safe = search_name.upper().replace('"', '""')
    cmd = (
        f'S I="" F  S I=$O({global_name}I)) Q:I=""  '
        f'I $P($G({global_name}I,0)),"^",1)["{safe}" W I Q'
    )
    out = _run_mumps(cmd)
    ien = out.strip()
    return ien if ien and ien.isdigit() else None


@app.route("/api/clinical/vital", methods=["POST"])
def clinical_add_vital():
    """Add a new vital measurement to MUMPS."""
    data = request.get_json(silent=True) or {}
    dfn = str(data.get("patient_dfn", ""))
    vital_name = data.get("vital_type", "")
    reading = str(data.get("reading", ""))

    if not dfn or not _validate_ien(dfn):
        return jsonify({"error": "Valid patient_dfn required"}), 400
    if not reading:
        return jsonify({"error": "reading required"}), 400

    type_ien = VITAL_TYPES.get(vital_name.upper())
    if not type_ien:
        return jsonify({"error": f"Unknown vital_type: {vital_name}",
                        "valid_types": list(VITAL_TYPES.keys())}), 400

    new_ien = _next_ien("^GMR(120.5,")
    fm_now = _fm_date_now()
    safe_reading = reading.replace('"', '""')

    # ^GMR(120.5,IEN,0) = date_taken^patient_dfn^vital_type^date_entered^location^entered_by^^rate
    node0 = f'{fm_now}^{dfn}^{type_ien}^{fm_now}^^^^{safe_reading}'
    cmd = f'S ^GMR(120.5,{new_ien},0)="{node0}"'
    _run_mumps(cmd)

    verify = _run_mumps(f'W $G(^GMR(120.5,{new_ien},0))')
    return jsonify({
        "success": True,
        "ien": new_ien,
        "global_ref": f"^GMR(120.5,{new_ien})",
        "stored": verify.strip(),
        "vital_type": vital_name,
        "reading": reading,
    })


@app.route("/api/clinical/problem", methods=["POST"])
def clinical_add_problem():
    """Add a new problem to MUMPS."""
    data = request.get_json(silent=True) or {}
    dfn = str(data.get("patient_dfn", ""))
    narrative = data.get("narrative", "")
    status = data.get("status", "A")
    date_onset = data.get("date_onset", "")

    if not dfn or not _validate_ien(dfn):
        return jsonify({"error": "Valid patient_dfn required"}), 400
    if not narrative:
        return jsonify({"error": "narrative required"}), 400
    if status not in ("A", "I"):
        return jsonify({"error": "status must be A or I"}), 400

    narr_ien = _lookup_ien("^AUTNPOV(", narrative)
    if not narr_ien:
        narr_ien = ""

    new_ien = _next_ien("^AUPNPROB(")
    fm_now = _fm_date_now()
    fm_onset = _iso_to_fm(date_onset)

    # Count existing problems for this patient to get problem_number
    count_out = _run_mumps(
        f'S C=0,I="" F  S I=$O(^AUPNPROB(I)) Q:I=""  '
        f'I $P($G(^AUPNPROB(I,0)),"^",2)="{dfn}" S C=C+1\nW C'
    )
    try:
        prob_num = str(int(count_out.strip()) + 1)
    except (ValueError, TypeError):
        prob_num = "1"

    safe_narr = narrative.upper().replace('"', '""')

    # Node 0: diagnosis_ptr^patient_dfn^date_modified^^narrative_ptr^facility^problem_num^date_entered^^^^status^date_onset
    node0 = f'^{dfn}^{fm_now}^^{narr_ien}^500^{prob_num}^{fm_now}^^^^{status}^{fm_onset}'
    # Node 1: lexicon_term^condition^...^date_recorded^...
    node1 = f'{safe_narr}^T^^^^^^^^{fm_now}'

    cmd = (
        f'S ^AUPNPROB({new_ien},0)="{node0}" '
        f'S ^AUPNPROB({new_ien},1)="{node1}"'
    )
    _run_mumps(cmd)

    verify0 = _run_mumps(f'W $G(^AUPNPROB({new_ien},0))')
    verify1 = _run_mumps(f'W $G(^AUPNPROB({new_ien},1))')
    return jsonify({
        "success": True,
        "ien": new_ien,
        "global_ref": f"^AUPNPROB({new_ien})",
        "node_0": verify0.strip(),
        "node_1": verify1.strip(),
        "narrative": narrative,
        "status": status,
    })


@app.route("/api/clinical/problem/<ien>/inactivate", methods=["POST"])
def clinical_inactivate_problem(ien: str):
    """Inactivate a problem (set status to I)."""
    if not _validate_ien(ien):
        return jsonify({"error": "IEN must be numeric"}), 400

    before = _run_mumps(f'W $G(^AUPNPROB({ien},0))').strip()
    if not before:
        return jsonify({"error": "Problem not found"}), 404

    fm_now = _fm_date_now()
    # Set status (piece 12) to I and update date_modified (piece 3)
    cmd = (
        f'S $P(^AUPNPROB({ien},0),"^",12)="I" '
        f'S $P(^AUPNPROB({ien},0),"^",3)="{fm_now}"'
    )
    _run_mumps(cmd)

    after = _run_mumps(f'W $G(^AUPNPROB({ien},0))').strip()
    return jsonify({
        "success": True,
        "ien": ien,
        "global_ref": f"^AUPNPROB({ien})",
        "before": before,
        "after": after,
    })


@app.route("/api/clinical/allergy", methods=["POST"])
def clinical_add_allergy():
    """Add a new allergy to MUMPS."""
    data = request.get_json(silent=True) or {}
    dfn = str(data.get("patient_dfn", ""))
    reactant = data.get("reactant", "")
    allergy_type = data.get("allergy_type", "D")
    mechanism = data.get("mechanism", "ALLERGY")

    if not dfn or not _validate_ien(dfn):
        return jsonify({"error": "Valid patient_dfn required"}), 400
    if not reactant:
        return jsonify({"error": "reactant required"}), 400
    if allergy_type not in ("D", "F", "O"):
        return jsonify({"error": "allergy_type must be D(rug), F(ood), or O(ther)"}), 400

    new_ien = _next_ien("^GMR(120.8,")
    fm_now = _fm_date_now()
    safe_reactant = reactant.upper().replace('"', '""')
    safe_mech = mechanism.upper().replace('"', '""')

    # ^GMR(120.8,IEN,0) = patient_dfn^reactant^^origination_date^^originator^^^^^^^^^verified^^mechanism^allergy_type
    # pieces: 1=dfn, 2=reactant, 4=date, 14=verified, 17=mechanism, 18=type
    parts = [""] * 18
    parts[0] = dfn
    parts[1] = safe_reactant
    parts[3] = fm_now
    parts[13] = "0"
    parts[16] = safe_mech
    parts[17] = allergy_type
    node0 = "^".join(parts)

    cmd = f'S ^GMR(120.8,{new_ien},0)="{node0}"'
    _run_mumps(cmd)

    verify = _run_mumps(f'W $G(^GMR(120.8,{new_ien},0))')
    return jsonify({
        "success": True,
        "ien": new_ien,
        "global_ref": f"^GMR(120.8,{new_ien})",
        "stored": verify.strip(),
        "reactant": reactant,
        "allergy_type": allergy_type,
        "mechanism": mechanism,
    })


@app.route("/api/clinical/lookups/<table>")
def clinical_lookups(table: str):
    """Return lookup values for dropdowns (vital_types, etc.)."""
    if table == "vital_types":
        return jsonify({"values": list(VITAL_TYPES.keys())})
    return jsonify({"error": f"Unknown lookup: {table}"}), 404


# ── Live MUMPS reads (reflects writes immediately) ───────────

VITAL_NAMES = {v: k for k, v in VITAL_TYPES.items()}


def _fm_to_iso(fm: str) -> str:
    """Convert FileMan date to ISO-ish string."""
    if not fm or len(fm) < 7:
        return ""
    try:
        yr = int(fm[:3]) + 1700
        mo = fm[3:5]
        dy = fm[5:7]
        result = f"{yr}-{mo}-{dy}"
        if "." in fm:
            t = fm.split(".")[1].ljust(6, "0")
            result += f" {t[0:2]}:{t[2:4]}"
        return result
    except (ValueError, IndexError):
        return fm


@app.route("/api/live/patient/<dfn>/problems")
def live_problems(dfn: str):
    """Read problems directly from MUMPS (reflects writes immediately)."""
    if not _validate_ien(dfn):
        return jsonify({"error": "DFN must be numeric"}), 400

    cmd = (
        f'S I="" F  S I=$O(^AUPNPROB(I)) Q:I=""  '
        f'S V=$G(^AUPNPROB(I,0)) '
        f'I $P(V,"^",2)="{dfn}" '
        f'W "R:",I,"||",$G(^AUPNPROB(I,0)),"||",$G(^AUPNPROB(I,1)),!'
    )
    out = _run_mumps(cmd, timeout=15)
    probs = []
    for line in out.split("\n"):
        if not line.startswith("R:"):
            continue
        parts = line[2:].split("||", 2)
        if len(parts) < 2:
            continue
        ien = parts[0]
        n0 = parts[1].split("^") if parts[1] else []
        n1 = parts[2].split("^") if len(parts) > 2 and parts[2] else []

        def p(arr, idx):
            return arr[idx] if idx < len(arr) else ""

        probs.append({
            "id": ien,
            "narrative": p(n1, 0) or p(n0, 4),
            "diagnosis": p(n0, 0),
            "status": p(n0, 11),
            "date_onset": _fm_to_iso(p(n0, 12)),
            "date_entered": _fm_to_iso(p(n0, 7)),
            "date_resolved": _fm_to_iso(p(n1, 6)),
            "date_modified": _fm_to_iso(p(n0, 2)),
            "provider": p(n1, 4),
            "priority": p(n1, 13),
            "condition": p(n1, 1),
            "sc": p(n1, 9) == "1",
            "source": "mumps",
        })
    probs.sort(key=lambda x: (0 if x["status"] == "A" else 1))
    return jsonify({"problems": probs, "source": "mumps"})


@app.route("/api/live/patient/<dfn>/vitals")
def live_vitals(dfn: str):
    """Read vitals directly from MUMPS."""
    if not _validate_ien(dfn):
        return jsonify({"error": "DFN must be numeric"}), 400

    cmd = (
        f'S I="" F  S I=$O(^GMR(120.5,I)) Q:I=""  '
        f'S V=$G(^GMR(120.5,I,0)) '
        f'I $P(V,"^",2)="{dfn}" '
        f'W "R:",I,"||",V,!'
    )
    out = _run_mumps(cmd, timeout=15)
    vitals_list = []
    for line in out.split("\n"):
        if not line.startswith("R:"):
            continue
        parts = line[2:].split("||", 1)
        if len(parts) < 2:
            continue
        ien = parts[0]
        pieces = parts[1].split("^")

        def p(idx):
            return pieces[idx] if idx < len(pieces) else ""

        vitals_list.append({
            "id": ien,
            "datetime_taken": _fm_to_iso(p(0)),
            "vital_name": VITAL_NAMES.get(p(2), p(2)),
            "reading": p(7),
            "location": p(4),
            "entered_by": p(5),
            "source": "mumps",
        })
    vitals_list.sort(key=lambda x: x["datetime_taken"], reverse=True)
    return jsonify({"vitals": vitals_list, "source": "mumps"})


@app.route("/api/live/patient/<dfn>/allergies")
def live_allergies(dfn: str):
    """Read allergies directly from MUMPS."""
    if not _validate_ien(dfn):
        return jsonify({"error": "DFN must be numeric"}), 400

    cmd = (
        f'S I="" F  S I=$O(^GMR(120.8,I)) Q:I=""  '
        f'S V=$G(^GMR(120.8,I,0)) '
        f'I $P(V,"^",1)="{dfn}" '
        f'W "R:",I,"||",V,!'
    )
    out = _run_mumps(cmd, timeout=15)
    allergy_list = []
    for line in out.split("\n"):
        if not line.startswith("R:"):
            continue
        parts = line[2:].split("||", 1)
        if len(parts) < 2:
            continue
        ien = parts[0]
        pieces = parts[1].split("^")

        def p(idx):
            return pieces[idx] if idx < len(pieces) else ""

        atype = p(17)
        allergy_list.append({
            "id": ien,
            "reactant": p(1),
            "allergy_type": atype,
            "entry_date": _fm_to_iso(p(3)),
            "mechanism": p(16),
            "verified": p(13) == "1",
            "source": "mumps",
        })
    return jsonify({"allergies": allergy_list, "source": "mumps"})


# ── Main ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)
