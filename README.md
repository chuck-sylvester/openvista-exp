# OpenVistA Exp

This sample application is based on the Python/Flask application Developed by DukeDeSouth:  
[https://github.com/DukeDeSouth/openvista-explorer](https://github.com/DukeDeSouth/openvista-explorer)

This version ports the application from Flask to FastAPI. Application functionality, UI, and UX have not changed and use the original source code from the repository referenced above. Source VistA data was generated via a new and separate mechanism and is not affiliated with the original reference application.  

Original Readme content below

---

A web-based tool for exploring VistA/MUMPS global structures using real VEHU test data.

**Live demo:** [openvista.cc/app](https://openvista.cc/app)

## What it does

- Browse 193,900+ clinical records from VistA VEHU across 15 packages
- View raw MUMPS globals with piece-by-piece breakdowns in a side panel
- Write vitals, problems, and allergies directly to live MUMPS globals
- See FileMan date formats, pointer resolution, IEN allocation in action

## Screenshot

The app shows a clinical patient view on the left with a MUMPS globals panel on the right, displaying the raw `^GMR(120.5)`, `^DPT`, `^AUPNPROB` structures behind the clinical data.

## Stack

- **Frontend:** Single-file HTML/CSS/JS
- **Backend:** Python/Flask with SQLAlchemy Core
- **Database:** PostgreSQL 17 (bulk reads) + live MUMPS via YottaDB (writes and live panel)
- **MUMPS:** VistA VEHU on YottaDB ([OSEHRA VEHU Docker image](https://hub.docker.com/r/yottadb/octo-vehu))

## Packages covered

| Package | Global | Records |
|---------|--------|---------|
| Patients | ^DPT | Demographics, service history |
| Problems | ^AUPNPROB | Problem list with status tracking |
| Vitals | ^GMR(120.5) | Vital signs with type resolution |
| Allergies | ^GMR(120.8) | Allergy/adverse reactions |
| Pharmacy | ^PSRX | Prescriptions, refills, status |
| Labs | ^LR | Lab results, panels, ranges |
| Orders | ^OR(100) | CPOE orders with status |
| Notes | ^TIU(8925) | TIU clinical documents |
| Consults | ^GMR(123) | Consult requests and results |
| Radiology | ^RADPT | Rad exams and reports |
| Scheduling | ^SCE | Appointments |
| Surgery | ^SRF | Surgical cases |
| Immunizations | ^AUPNIMM | Vaccination records |
| Mental Health | ^YTT | MH instruments and scores |
| PCE | ^AUPNVSIT | Visits, procedures, diagnoses |

## Write operations

The app supports writing to live MUMPS globals for:
- **Vitals** — Enter vital signs → `^GMR(120.5)`
- **Problems** — Add/inactivate problems → `^AUPNPROB`
- **Allergies** — Add allergy records → `^GMR(120.8)`

After each write, data is read back from MUMPS to verify persistence.

## Setup

### Prerequisites
- Python 3.10+
- PostgreSQL 17
- Docker (for VistA VEHU container)

### Run VEHU
```bash
docker run -d --name vista-vehu \
  --restart unless-stopped \
  download.yottadb.com/db/octo-vehu:latest-master
```

### Install and run
```bash
# Python dependencies
pip install flask sqlalchemy psycopg2-binary gunicorn

# Environment variable
export DATABASE_URL="postgresql://user:pass@localhost/openvista"

# PostgreSQL loader
python migrate_db.py   # load VEHU JSON data into PostgreSQL

# Hosting service
gunicorn app:app -b 0.0.0.0:5005 -w 4
```

## Disclaimer

This is an **educational tool** for exploring VistA/MUMPS global structures.

**NOT intended for clinical use.** Write operations bypass FileMan validation and do not maintain cross-references, audit trails, or business rule enforcement. IEN allocation is simplified and does not use FileMan's native allocation.

For production VistA integration, use the RPC Broker, FileMan API (`^DIE`, `^DIK`), or a certified FHIR adapter.

## License

MIT

---

# FastAPI + Ninja2 Templates Setup

Additional Readme content re: FastAPI port

---

> Set DATABASE_URL via .env + config.py + Pydantic
> Variable: database_url

## Setup

### Prerequisites

> - Python v3.11.14
> - PostgreSQL 16
> - Docker (for PostgreSQL & VistA VEHU image)

### Run VEHU VistA

> Goal: use med-ydb / vehu-311 container
> Start: via Docker Desktop

