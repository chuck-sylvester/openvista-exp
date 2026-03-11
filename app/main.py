# ─────────────────────────────────────────────────────────────────
# app/main.py
# ─────────────────────────────────────────────────────────────────
# Staring point for openvista-explorer application
#
#   Run from root: uvicorn app.main:app --reload --port 8010
#      Access via: localhost:8010
#     Stop server: CTRL + C
# ─────────────────────────────────────────────────────────────────

# Main imports
from fastapi import FastAPI, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy import select, func
from typing import Dict, List, Optional

import logging

# Import 'settings' object from root-level config file
from config import settings

from etl.db import (
    adt_movements, allergies, appointments, consults, engine, exams,
    health_factors, immunizations, lab_results, labs, notes, orders,
    patient_education, patients, prescriptions, problems, procedures,
    rad_reports, skin_tests, surgeries, visit_diagnoses, visit_providers,
    vitals,
)

# Configure Python Logging
logging.basicConfig(
    level=settings.app.log_level.upper(),
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

print()
print(f"       Application Name: {settings.app.name}")
print(f"    Application Version: {settings.app.version}")
print(f"      Application Debug: {settings.app.debug}")
print(f"  Application Log Level: {settings.app.log_level}")
print(f"          Database Host: {settings.postgres.host}")
print(f"          Database Port: {settings.postgres.port}")
print(f"          Database Name: {settings.postgres.db}")
print(f"           Database URL: <top secret>")
# print(f"           Database URL: {settings.postgres.database_url}")
print()

# Initialize the FastAPI app
app = FastAPI(title=settings.app.name, debug=settings.app.debug)

# Mount the static files directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup Jinja2 templates directory with auto-reload for development
templates = Jinja2Templates(directory="app/templates")
templates.env.auto_reload = True

# Register all routers
# app.include_router(auth.router, tags=["auth"])
# app.include_router(dashboard.router, tags=["dashboard"])
# app.include_router(admin.router, tags=["admin"])
# app.include_router(health.router, tags=["health"])


PACKAGES = [
    "Patient Registration", "Problem List", "Vitals",
    "Allergy / Adverse Reaction", "Outpatient Pharmacy", "Lab Service",
    "Order Entry (CPOE)", "Consult Request Tracking", "Mental Health",
    "Radiology", "Inpatient Medications", "PCE Patient Care Encounter",
    "TIU Clinical Notes", "Health Summary", "Scheduling",
]


# Create root route handler
@app.get("/")
async def root():
    """Redirect to marketing landing page."""
    return RedirectResponse(url="/landing")


# Landing / marketing page
@app.get("/landing", response_class=HTMLResponse)
async def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})


# Main App root
@app.get("/app", response_class=HTMLResponse)
async def main_app(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/overview")
async def get_overview():
    tables_to_count = [
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
    ]

    counts: Dict[str, int] = {}

    with engine.connect() as conn:
        for name, table in tables_to_count:
            # .scalar() returns the first column of the first row
            result = conn.execute(select(func.count()).select_from(table)).scalar()
            counts[name] = result or 0

    return {
        "system": "OpenVistA",
        "source": "VistA VEHU — real MUMPS globals",
        "packages": len(PACKAGES),
        "package_list": PACKAGES,
        "data": counts,
        "total_records": sum(counts.values()),
    }



@app.get("/api/patients")
async def patients_list(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    search: str = Query("", alias="search")
):
    search_term = search.upper()

    with engine.connect() as conn:
        # Build the base query
        base = select(patients)
        if search_term:
            base = base.where(patients.c.name.ilike(f"%{search_term}%"))

        # Calculate total count
        total = conn.execute(
            select(func.count()).select_from(base.subquery())
        ).scalar() or 0

        # Execute paginated query
        rows = conn.execute(
            base.order_by(patients.c.dfn)
            .limit(per_page)
            .offset((page - 1) * per_page)
        ).fetchall()

    return {
        "patients": [_patient_summary(r) for r in rows],
        "pagination": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page if total > 0 else 0,
        },
    }

# Standard health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": settings.app.name}


# Simple route handler
@app.get("/hello", response_class=HTMLResponse)
async def hello_htmx():
    return"<p class='success-msg'>HTMX is working! Connection successful.</p>"
