"""VistA Clinical Models — 15 packages, 89 specifications.

Extracted from VistA (3.7M LOC MUMPS, 1966-present).
Data source: VistA VEHU training database.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# ── Allergy ──────────────────────────────────────────────

@dataclass
class Allergy:
    """Patient allergy/adverse reaction record.
    Types: D=Drug, F=Food, O=Other. Mechanism: allergy or intolerance.
    Source: ^GMR(120.8,...) (file #120.8, VistA Adverse Reaction Tracking)
    """
    ien: int
    patient_dfn: int = 0
    reactant: str = ""
    allergen_ptr: Optional[int] = None
    entry_date: str = ""
    originator: Optional[int] = None
    observed_historical: str = ""
    allergy_type: str = ""
    mechanism: str = ""
    severity: Optional[int] = None
    signed_off: bool = False
    verified: bool = False
    verified_by: Optional[int] = None
    verification_date: str = ""
    entered_in_error: bool = False
    eie_date: str = ""
    eie_user: Optional[int] = None


# ── Appointment ────────────────────────────────────────────

@dataclass
class Appointment:
    """Appointment with dual storage: clinic-side in ^SC and patient-side in ^DPT.
    Source: ^SC(clinic,\"S\",date) file #44.003, ^DPT(DFN,\"S\",date) file #2.98
    (VistA Scheduling)
    """
    patient_dfn: int = 0
    clinic_ien: int = 0
    appointment_datetime: str = ""
    length_minutes: int = 0
    status: str = ""
    appointment_type: Optional[int] = None
    overbook: bool = False
    consult_ien: Optional[int] = None
    checkin_datetime: str = ""
    checkout_datetime: str = ""
    encounter_ien: Optional[int] = None
    made_by: Optional[int] = None
    date_made: str = ""
    cancel_reason: Optional[int] = None
    cancel_remarks: str = ""
    cancel_datetime: str = ""
    noshow_datetime: str = ""
    noshow_user: Optional[int] = None


# ── Consult ────────────────────────────────────────────────

@dataclass
class Consult:
    """Consult request tracking record.
    Status: 5=Pending 6=Active 2=Complete 1=Cancelled 8=Scheduled.
    Source: ^GMR(123,...) (file #123, VistA Consult Request Tracking)
    """
    ien: int = 0
    patient_dfn: int = 0
    order_ien: Optional[int] = None
    service: Optional[int] = None
    procedure: Optional[int] = None
    requesting_provider: Optional[int] = None
    ordering_provider: Optional[int] = None
    date_of_request: str = ""
    status: Optional[int] = None
    cprs_order: Optional[int] = None
    reason_for_request: str = ""
    significant_findings: str = ""
    provider_diagnosis: str = ""
    icd_code: str = ""
    last_action: Optional[int] = None


# ── Inpatient Medication ──────────────────────────────────

@dataclass
class InpatientMed:
    """Inpatient medication order for a hospitalized patient.
    Includes unit dose and IV medications.
    Source: ^PS(55,DFN,...) (file #55, VistA Inpatient Medications)
    """
    ien: int = 0
    patient_dfn: int = 0
    drug: Optional[int] = None
    dose: str = ""
    route: Optional[int] = None
    schedule: str = ""
    start_datetime: str = ""
    stop_datetime: str = ""
    ordering_provider: Optional[int] = None
    verifying_pharmacist: Optional[int] = None
    status: str = ""
    order_type: str = ""
    ward: Optional[int] = None
    administration_times: str = ""
    special_instructions: str = ""


# ── Lab Order ──────────────────────────────────────────────

@dataclass
class LabOrder:
    """Lab order record. Collection type: WC=Ward Collect LC=Lab Collect SP=Send Patient.
    Urgency: ROUTINE STAT ASAP. Status: ordered/collected/accessioned.
    Source: ^LRO(69,...) (file #69, VistA Lab Service)
    """
    ien: int = 0
    patient_dfn: int = 0
    lrdfn: Optional[int] = None
    order_date: str = ""
    specimen_number: Optional[int] = None
    test: Optional[int] = None
    specimen_type: Optional[int] = None
    collection_type: str = ""
    urgency: str = ""
    ordering_provider: Optional[int] = None
    location: Optional[int] = None
    collection_datetime: str = ""
    status: str = ""
    combined_order: bool = False
    division: Optional[int] = None


# ── Lab Accession ──────────────────────────────────────────

@dataclass
class LabAccession:
    """Lab accession record.
    Source: ^LRO(68,...) (file #68, VistA Lab Service)
    """
    accession_area: Optional[int] = None
    accession_date: str = ""
    accession_number: Optional[int] = None
    lrdfn: Optional[int] = None
    order_date: str = ""
    specimen_number: Optional[int] = None
    uid: str = ""
    collection_datetime: str = ""
    inverse_datetime: str = ""
    location: Optional[int] = None


# ── Lab Result ─────────────────────────────────────────────

@dataclass
class LabResult:
    """Lab result record. LRIDT is inverse datetime (9999999-datetime).
    Abnormal flag: H L HH LL. Reference range: low!high format.
    Source: ^LR(LRDFN,'CH',LRIDT,...) (file #63, VistA Lab Service)
    """
    lrdfn: int = 0
    inverse_datetime: str = ""
    test_dataname: Optional[int] = None
    result_value: str = ""
    abnormal_flag: str = ""
    reference_range: str = ""
    units: str = ""
    collection_datetime: str = ""
    verified: bool = False
    verifying_tech: Optional[int] = None
    verified_datetime: str = ""
    specimen_type: Optional[int] = None
    accession_number: Optional[int] = None
    performing_lab: Optional[int] = None
    method: str = ""


# ── Mental Health Administration ───────────────────────────

@dataclass
class MhAdministration:
    """Mental health instrument administration record.
    Source: ^YTT(601.84,...) (file #601.84, VistA Mental Health)
    """
    ien: int = 0
    patient_dfn: int = 0
    instrument: Optional[int] = None
    date_given: str = ""
    is_complete: bool = False
    order_ien: Optional[int] = None
    location: Optional[int] = None
    scoring_version: Optional[int] = None
    saved: bool = False
    administered_by: Optional[int] = None
    total_score: Optional[int] = None
    interpretation: str = ""


# ── Mental Health Result ───────────────────────────────────

@dataclass
class MhResult:
    """Mental health instrument result by scale.
    Source: ^YTT(601.92,...) (file #601.92, VistA Mental Health)
    """
    ien: int = 0
    administration_ien: int = 0
    scale_name: str = ""
    raw_score: Optional[int] = None
    transformed_score: Optional[int] = None
    scale_group: Optional[int] = None
    percentile: Optional[int] = None
    interpretation: str = ""


# ── Order ──────────────────────────────────────────────────

@dataclass
class Order:
    """Generic order record. All VistA order types share this common structure.
    Status: 1=DC 2=Complete 3=Hold 5=Pending 6=Active 7=Expired 8=Flagged 10=Delayed
    11=Unreleased 12=Changed 13=Cancelled 14=Lapsed 15=Renewed.
    Source: ^OR(100,...) (file #100, VistA CPOE)
    """
    ien: int = 0
    patient_dfn: int = 0
    provider: Optional[int] = None
    dialog: Optional[int] = None
    entered_by: Optional[int] = None
    log_datetime: str = ""
    start_datetime: str = ""
    stop_datetime: str = ""
    location: Optional[int] = None
    display_group: Optional[int] = None
    category: str = ""
    package: Optional[int] = None
    urgency: Optional[int] = None
    status: Optional[int] = None
    last_activity: str = ""
    current_action: str = ""
    parent_order: Optional[int] = None
    order_text: str = ""
    nature_of_order: Optional[int] = None
    signature_required: bool = False


# ── Patient ────────────────────────────────────────────────

@dataclass
class Patient:
    """Core patient demographics. Referenced by every clinical package in VistA.
    Name format: LAST,FIRST MIDDLE SUFFIX. SSN can be pseudo (P) with reason.
    Source: ^DPT (file #2, VistA Registration)
    """
    dfn: int
    name: str = ""
    sex: str = ""
    dob: str = ""
    ssn: str = ""
    marital_status: Optional[int] = None
    religion: Optional[int] = None
    occupation: str = ""
    who_entered: Optional[int] = None
    date_entered: str = ""
    street_1: str = ""
    street_2: str = ""
    city: str = ""
    state: Optional[int] = None
    zip: str = ""
    bad_address: Optional[int] = None
    phone_home: str = ""
    phone_work: str = ""
    phone_cell: str = ""
    email: str = ""
    service_connected: bool = False
    sc_percentage: Optional[int] = None
    veteran: bool = False


# ── Prescription ──────────────────────────────────────────

@dataclass
class Prescription:
    """Outpatient prescription record.
    Status: 0=Active 1=NonVerified 3=Hold 5=Suspended 11=Expired 12=DC'd 13=Deleted.
    Mail window: W=Window M=Mail.
    Source: ^PSRX (file #52, VistA Outpatient Pharmacy)
    """
    ien: int = 0
    rx_number: str = ""
    patient_dfn: int = 0
    patient_status: Optional[int] = None
    provider: Optional[int] = None
    clinic: Optional[int] = None
    drug: Optional[int] = None
    quantity: int = 0
    days_supply: int = 0
    refills_authorized: int = 0
    mail_window: str = ""
    issue_date: str = ""
    sig: str = ""
    login_date: str = ""
    fill_date: str = ""
    pharmacist: Optional[int] = None
    dispensed_date: str = ""
    stop_date: str = ""
    ndc: str = ""
    division: Optional[int] = None
    released_date: str = ""
    status: Optional[int] = None
    last_dispensed_date: str = ""
    discontinue_date: str = ""
    remarks: str = ""
    hold_reason: str = ""
    pki_signed: bool = False


# ── Problem ────────────────────────────────────────────────

@dataclass
class Problem:
    """Patient problem record from VistA Problem List.
    Source: ^AUPNPROB (file #9000011, VistA Problem List)
    """
    ifn: int = 0
    diagnosis_ptr: Optional[int] = None
    patient_dfn: int = 0
    date_modified: str = ""
    narrative_ptr: Optional[int] = None
    facility: Optional[int] = None
    problem_number: Optional[int] = None
    date_entered: str = ""
    status: str = ""
    date_onset: str = ""
    lexicon_term: Optional[int] = None
    condition: str = ""
    recording_provider: Optional[int] = None
    initial_provider: Optional[int] = None
    responsible_provider: Optional[int] = None
    service: Optional[int] = None
    date_resolved: str = ""
    clinic: Optional[int] = None
    date_recorded: str = ""
    sc: bool = False
    ao: bool = False
    ir: bool = False
    ec: bool = False
    priority: str = ""
    hnc: bool = False
    mst: bool = False
    cv: bool = False
    shad: bool = False
    snomed_concept: str = ""
    snomed_designation: str = ""
    code_date: str = ""
    coding_system: str = ""


# ── Radiology Order ────────────────────────────────────────

@dataclass
class RadOrder:
    """Radiology order record.
    Order status: PENDING/COMPLETE/HOLD/CANCELLED. Urgency: ROUTINE/STAT/ASAP.
    Source: ^RAO(75.1,...) (file #75.1, VistA Radiology)
    """
    ien: int = 0
    patient_dfn: int = 0
    procedure: Optional[int] = None
    order_status: str = ""
    request_date: str = ""
    desired_date: str = ""
    urgency: str = ""
    requesting_provider: Optional[int] = None
    requesting_location: Optional[int] = None
    clinical_history: str = ""
    imaging_type: str = ""
    reason_for_study: str = ""


# ── Radiology Exam ─────────────────────────────────────────

@dataclass
class RadExam:
    """Radiology exam record.
    Imaging types: CR/CT/MR/US/NM. Exam status: WAITING/EXAMINED/COMPLETE/CANCELLED.
    Report status: DRAFT/VERIFIED/RELEASED.
    Source: ^RADPT(DFN,'DT',DTTM,'P',...) (file #70, VistA Radiology)
    """
    patient_dfn: int = 0
    exam_datetime: str = ""
    case_number: Optional[int] = None
    procedure: Optional[int] = None
    imaging_type: str = ""
    exam_status: str = ""
    requesting_location: Optional[int] = None
    requesting_provider: Optional[int] = None
    radiologist: Optional[int] = None
    report_status: str = ""
    credit_method: str = ""
    contrast_used: bool = False
    clinical_history: str = ""
    order_ien: Optional[int] = None
    division: Optional[int] = None


# ── TIU Document ───────────────────────────────────────────

@dataclass
class TiuDocument:
    """Clinical note/document. Status: 5=unsigned 6=uncosigned 7=completed 8=amended
    13=retracted 15=purged.
    Source: ^TIU(8925,...) (file #8925, VistA Text Integration Utility)
    """
    ien: int = 0
    patient_dfn: int = 0
    document_date: str = ""
    document_type: Optional[int] = None
    status: Optional[int] = None
    parent_document: Optional[int] = None
    author: Optional[int] = None
    expected_cosigner: Optional[int] = None
    visit: Optional[int] = None
    location: Optional[int] = None
    text: str = ""
    signature_date: str = ""


# ── Visit ──────────────────────────────────────────────────

@dataclass
class Visit:
    """Patient Care Encounter visit record. Links clinical events for a patient contact.
    Source: ^AUPNVSIT(9000010,...) (file #9000010, VistA PCE)
    """
    ien: int = 0
    visit_datetime: str = ""
    patient_dfn: int = 0
    encounter_type: str = ""
    stop_code: Optional[int] = None
    hospital_location: Optional[int] = None
    pce_status: str = ""
    division: Optional[int] = None
    parent_visit: Optional[int] = None
    service_category: str = ""
    created_by: Optional[int] = None
    check_out_datetime: str = ""


# ── Vital Measurement ─────────────────────────────────────

@dataclass
class VitalMeasurement:
    """Single vital sign measurement. Types: BP, T, P, R, HT, WT, PN, PO2, BMI, etc.
    Source: ^GMR(120.5,...) (file #120.5, VistA GMR Vital Measurement)
    """
    ien: int = 0
    datetime_taken: str = ""
    patient_dfn: int = 0
    vital_type: Optional[int] = None
    datetime_entered: str = ""
    hospital_location: Optional[int] = None
    entered_by: Optional[int] = None
    reading: str = ""
    supplemental_o2: str = ""
    entered_in_error: bool = False
    error_marked_by: Optional[int] = None
    error_reason: Optional[int] = None
    qualifiers: list = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════
# Operations
# ═══════════════════════════════════════════════════════════════


# ── Operations: Allergy ────────────────────────────────────

def vista_add_allergy(
    patient_dfn: int,
    reactant: str,
    allergy_type: str,
    observed_historical: str,
    mechanism: str,
    originator: int,
    severity: Optional[int] = None,
    signs_symptoms: Optional[list] = None,
) -> dict:
    """Add a new allergy/adverse reaction for a patient.
    Creates ^GMR(120.8) record. Source: GMRAPES1:ADAR, GMRAGUI1:UPDATE
    (VistA Adverse Reaction Tracking)
    """
    ...


def vista_add_allergy_comment(
    allergy_ien: int,
    comment_text: str,
    comment_author: int,
) -> dict:
    """Add a comment to an existing allergy record.
    Source: GMRAFX:ADCOM, GMRAGUI1:ADCOM (VistA Adverse Reaction Tracking)
    """
    ...


def vista_list_allergies(patient_dfn: int, include_eie: bool = False) -> dict:
    """List all allergies for a patient. Excludes entered-in-error by default.
    Source: GMRADSP1, GMRAOR2:GETREC (VistA Adverse Reaction Tracking)
    """
    ...


def vista_mark_allergy_error(allergy_ien: int, marked_by: int) -> dict:
    """Mark an allergy as entered-in-error.
    Source: GMRADEL:EIE, GMRAGUI1:EIE (VistA Adverse Reaction Tracking)
    """
    ...


def vista_verify_allergy(allergy_ien: int, verifier: int) -> dict:
    """Verify a patient allergy record.
    Source: GMRAVFY (VistA Adverse Reaction Tracking)
    """
    ...


# ── Operations: Consults ────────────────────────────────────

def vista_request_consult(
    patient_dfn: int,
    service: int,
    requesting_provider: int,
    reason_for_request: str,
    urgency: Optional[str] = None,
) -> dict:
    """Request a consult for a patient. Creates consult with status Pending (5).
    Source: GMRCP (VistA Consult Request Tracking)
    """
    ...


def vista_receive_consult(consult_ien: int, receiving_provider: int) -> dict:
    """Receive a pending consult. Transitions status from Pending (5) to Active (6).
    Source: GMRCA:21 (VistA Consult Request Tracking)
    """
    ...


def vista_complete_consult(
    consult_ien: int,
    completing_provider: int,
    significant_findings: str,
) -> dict:
    """Complete an active consult. Transitions status to Complete (2).
    Source: GMRCAU:COMPLETE (VistA Consult Request Tracking)
    """
    ...


def vista_cancel_consult(consult_ien: int, cancel_reason: str) -> dict:
    """Cancel a consult. Transitions status to Cancelled (1).
    Source: GMRCA:19 (VistA Consult Request Tracking)
    """
    ...


def vista_add_consult_comment(
    consult_ien: int,
    comment_text: str,
    author: int,
) -> dict:
    """Add a comment to a consult.
    Source: GMRCP:COMMENT (VistA Consult Request Tracking)
    """
    ...


# ── Operations: Health Summary ──────────────────────────────

def vista_generate_health_summary(
    patient_dfn: int,
    summary_type: str,
) -> dict:
    """Generate a comprehensive health summary for a patient.
    Aggregates data from problems, vitals, allergies, medications, lab, appointments.
    Source: GMTS (VistA Health Summary)
    """
    ...


# ── Operations: Inpatient Medications ───────────────────────

def vista_order_inpatient_med(
    patient_dfn: int,
    drug: int,
    dose: str,
    route: int,
    schedule: str,
    ordering_provider: int,
    ward: int,
) -> dict:
    """Order an inpatient medication for an admitted patient.
    Source: PSJI (VistA Inpatient Medications)
    """
    ...


def vista_administer_med(
    med_ien: int,
    administering_nurse: int,
    administration_datetime: str,
) -> dict:
    """Record administration of an inpatient medication.
    Source: PSBMLU (VistA BCMA/Inpatient Medications)
    """
    ...


def vista_verify_inpatient_med(med_ien: int, pharmacist: int) -> dict:
    """Verify an inpatient medication order.
    Source: PSJVER (VistA Inpatient Medications)
    """
    ...


def vista_hold_inpatient_med(med_ien: int, hold_reason: str) -> dict:
    """Place an active inpatient medication on hold.
    Source: PSJHOLD (VistA Inpatient Medications)
    """
    ...


def vista_dc_inpatient_med(
    med_ien: int,
    reason: str,
    discontinued_by: int,
) -> dict:
    """Discontinue an inpatient medication order.
    Source: PSJDC (VistA Inpatient Medications)
    """
    ...


# ── Operations: Lab ────────────────────────────────────────

def vista_order_lab(
    patient_dfn: int,
    test: int,
    ordering_provider: int,
    specimen_type: Optional[int] = None,
    collection_type: Optional[str] = None,
    urgency: Optional[str] = None,
    location: Optional[int] = None,
) -> dict:
    """Order a lab test for a patient. Creates lab order in file #69.
    Source: LROW→LROW2 (VistA Lab Service)
    """
    ...


def vista_collect_specimen(order_ien: int, collector: int) -> dict:
    """Collect specimen for a lab order. Updates status to collected.
    Source: LROE→LROE1 (VistA Lab Service)
    """
    ...


def vista_enter_lab_results(
    lrdfn: int,
    test_dataname: int,
    result_value: str,
    performing_lab: Optional[int] = None,
) -> dict:
    """Enter lab result for a test.
    Source: LRVER→LRVR3 (VistA Lab Service)
    """
    ...


def vista_verify_lab_results(
    lrdfn: int,
    inverse_datetime: str,
    verifying_tech: int,
) -> dict:
    """Verify lab results.
    Source: LRVR→LRVR2 (VistA Lab Service)
    """
    ...


def vista_list_lab_results(
    patient_dfn: int,
    date_range_start: Optional[str] = None,
    date_range_end: Optional[str] = None,
) -> dict:
    """Retrieve lab results for a patient within a date range.
    Source: LR7OB63 (VistA Lab Service)
    """
    ...


# ── Operations: Mental Health ──────────────────────────────

def vista_administer_mh_test(
    patient_dfn: int,
    instrument: int,
    administered_by: int,
    location: Optional[int] = None,
) -> dict:
    """Administer a mental health screening instrument to a patient.
    Source: YTS:C (VistA Mental Health)
    """
    ...


def vista_score_mh_test(administration_ien: int, answers: list) -> dict:
    """Score a mental health instrument administration.
    Source: YTSCORE:LDSCORES (VistA Mental Health)
    """
    ...


def vista_list_mh_results(patient_dfn: int) -> dict:
    """List mental health screening results for a patient.
    Source: YTQAPI (VistA Mental Health)
    """
    ...


# ── Operations: Orders ──────────────────────────────────────

def vista_place_order(
    patient_dfn: int,
    orderable_item: int,
    provider: int,
    start_datetime: Optional[str] = None,
    stop_datetime: Optional[str] = None,
    urgency: Optional[int] = None,
    location: Optional[int] = None,
    category: Optional[str] = None,
) -> dict:
    """Place a new order. Creates order with status Pending (5).
    Source: ORCSAVE:NEW→ORCSEND:NW (VistA CPOE)
    """
    ...


def vista_sign_order(
    order_ien: int,
    signing_provider: int,
    electronic_signature: str,
) -> dict:
    """Sign a pending order. Sets status=Active (6).
    Source: ORCSIGN→ORCSAVE2:SIGN (VistA CPOE)
    """
    ...


def vista_discontinue_order(
    order_ien: int,
    reason: str,
    discontinued_by: int,
) -> dict:
    """Discontinue an order. Sets status=1 (DC).
    Source: ORCSEND:DC (VistA CPOE)
    """
    ...


def vista_hold_order(order_ien: int) -> dict:
    """Place order on hold. Sets status=3 (Hold).
    Source: ORCSEND:HD (VistA CPOE)
    """
    ...


def vista_release_order(order_ien: int) -> dict:
    """Release order from hold. Sets status=6 (Active).
    Source: ORCSEND:RL (VistA CPOE)
    """
    ...


def vista_flag_order(order_ien: int, flag_reason: str) -> dict:
    """Flag an order. Sets status=8 (Flagged).
    Source: ORCFLAG:EN (VistA CPOE)
    """
    ...


def vista_list_orders(
    patient_dfn: int,
    status_filter: Optional[str] = None,
) -> dict:
    """List all orders for a patient.
    Source: ^OR(100,'AC',...) (VistA CPOE)
    """
    ...


# ── Operations: Patient ─────────────────────────────────────

def vista_register_patient(
    name: str,
    sex: str,
    dob: str,
    ssn: str,
    entered_by: int,
    service_connected: Optional[bool] = None,
    veteran: Optional[bool] = None,
) -> dict:
    """Register a new patient in VistA.
    Source: VAFCPTAD:ADD, DPTLK4:FILE (VistA Registration)
    """
    ...


def vista_lookup_patient(search_term: str) -> dict:
    """Search for a patient by name, SSN, last 4, or first initial + last 4.
    Source: DPTLK, DPTLK1, DPTLK5 (VistA Registration)
    """
    ...


def vista_update_demographics(patient_dfn: int, changed_fields: dict) -> dict:
    """Update patient demographic information. Partial update only.
    Source: VAFCPTED:EDIT, DGRPE (VistA Registration)
    """
    ...


# ── Operations: PCE (Patient Care Encounter) ────────────────

def vista_create_visit(
    patient_dfn: int,
    visit_datetime: str,
    hospital_location: int,
    encounter_type: str,
    service_category: Optional[str] = None,
) -> dict:
    """Create a new Patient Care Encounter visit record.
    Source: PXAI:DATA2PCE (VistA PCE)
    """
    ...


def vista_add_visit_provider(
    visit_ien: int,
    provider: int,
    primary: Optional[bool] = None,
    person_class: Optional[str] = None,
) -> dict:
    """Add a provider to an existing visit.
    Source: PXAIPRV (VistA PCE)
    """
    ...


def vista_add_visit_diagnosis(
    visit_ien: int,
    icd_code: str,
    provider_narrative: Optional[str] = None,
    primary: Optional[bool] = None,
) -> dict:
    """Add a diagnosis (ICD code) to an existing visit.
    Source: PXAIPOV (VistA PCE)
    """
    ...


def vista_add_visit_procedure(
    visit_ien: int,
    cpt_code: str,
    provider: Optional[int] = None,
    modifier: Optional[str] = None,
    quantity: Optional[int] = None,
) -> dict:
    """Add a procedure (CPT code) to an existing visit.
    Source: PXAICPT (VistA PCE)
    """
    ...


# ── Operations: Pharmacy ────────────────────────────────────

def vista_new_prescription(
    patient_dfn: int,
    drug: int,
    sig: str,
    quantity: int,
    days_supply: int,
    refills: int,
    provider: int,
    mail_window: str,
    clinic: int,
) -> dict:
    """Create a new prescription.
    Source: PSONEW→PSON52 (VistA Outpatient Pharmacy)
    """
    ...


def vista_refill_prescription(
    rx_ien: int,
    pharmacist: int,
    mail_window: Optional[str] = None,
) -> dict:
    """Refill an existing prescription.
    Source: PSOREF→PSOR52 (VistA Outpatient Pharmacy)
    """
    ...


def vista_verify_prescription(rx_ien: int, pharmacist: int) -> dict:
    """Verify a non-verified prescription.
    Source: PSOVER→PSOVER1 (VistA Outpatient Pharmacy)
    """
    ...


def vista_hold_prescription(rx_ien: int, hold_reason: str) -> dict:
    """Place prescription on hold.
    Source: PSOCAN2:HLD (VistA Outpatient Pharmacy)
    """
    ...


def vista_suspend_prescription(rx_ien: int, suspense_date: str) -> dict:
    """Suspend a prescription.
    Source: PSORXL:SUS (VistA Outpatient Pharmacy)
    """
    ...


def vista_discontinue_prescription(
    rx_ien: int,
    reason: str,
    discontinued_by: int,
) -> dict:
    """Discontinue a prescription.
    Source: PSOCAN→PSOCAN3 (VistA Outpatient Pharmacy)
    """
    ...


def vista_reinstate_prescription(rx_ien: int) -> dict:
    """Reinstate a discontinued prescription.
    Source: PSOCAN2:REINS (VistA Outpatient Pharmacy)
    """
    ...


def vista_list_prescriptions(patient_dfn: int) -> dict:
    """List all prescriptions for a patient.
    Source: ^PS(55,DFN) (VistA Outpatient Pharmacy)
    """
    ...


# ── Operations: Problem List ────────────────────────────────

def vista_add_problem(
    patient: dict,
    narrative: str,
    diagnosis_ptr: int,
    responsible_provider: Optional[int] = None,
    recording_provider: Optional[int] = None,
    lexicon_term: Optional[int] = None,
    service: Optional[int] = None,
    clinic: Optional[int] = None,
    date_onset: Optional[str] = None,
    coding_system: Optional[str] = None,
    code_date: Optional[str] = None,
    snomed_concept: Optional[str] = None,
    snomed_designation: Optional[str] = None,
    sc: Optional[bool] = None,
    ao: Optional[bool] = None,
    ir: Optional[bool] = None,
    ec: Optional[bool] = None,
    hnc: Optional[bool] = None,
    mst: Optional[bool] = None,
    cv: Optional[bool] = None,
    shad: Optional[bool] = None,
) -> dict:
    """Add a new problem to patient's problem list.
    Source: GMPL1:ADD → GMPLSAVE:NEW (VistA Problem List)
    """
    ...


def vista_edit_problem(problem_ifn: int, changed_fields: dict) -> dict:
    """Edit fields of an existing problem. Supports partial update.
    Source: GMPLEDIT:EN → GMPLSAVE:EN (VistA Problem List)
    """
    ...


def vista_delete_problem(problem_ifn: int, reason: Optional[str] = None) -> dict:
    """Soft-delete a problem by setting condition to H (Hidden).
    Source: GMPL1:DELETE (VistA Problem List)
    """
    ...


def vista_inactivate_problem(
    problem_ifn: int,
    resolved_date: str,
    comment: Optional[str] = None,
) -> dict:
    """Inactivate an active problem. Sets status to I.
    Source: GMPL1:STATUS (VistA Problem List)
    """
    ...


def vista_verify_problem(problem_ifn: int) -> dict:
    """Verify a transcribed problem, changing condition T to P.
    Source: GMPL1:VERIFY (VistA Problem List)
    """
    ...


def vista_list_problems(
    patient_dfn: int,
    view_filter: str = "A",
) -> dict:
    """List problems for a patient. Filter: A=active I=inactive B=both R=removed.
    Source: GMPLMGR:BUILD → GMPLMGR1:GETPLIST (VistA Problem List)
    """
    ...


def vista_add_note(
    problem_ifn: int,
    note_text: str,
    facility: int,
    author: int,
) -> dict:
    """Add a comment/note to an existing problem.
    Source: GMPL1:NEWNOTE → GMPLSAVE:NEWNOTE (VistA Problem List)
    """
    ...


def vista_view_problem(problem_ifn: int) -> dict:
    """View full detail of a single problem.
    Source: GMPL:EXPAND (VistA Problem List)
    """
    ...


# ── Operations: Radiology ───────────────────────────────────

def vista_order_rad_exam(
    patient_dfn: int,
    procedure: int,
    requesting_provider: int,
    urgency: Optional[str] = None,
    requesting_location: Optional[int] = None,
    clinical_history: Optional[str] = None,
    imaging_type: Optional[str] = None,
) -> dict:
    """Order a radiology exam for a patient.
    Source: RAORD (VistA Radiology)
    """
    ...


def vista_register_rad_patient(order_ien: int, exam_datetime: str) -> dict:
    """Register a patient for radiology exam.
    Source: RAREG1 (VistA Radiology)
    """
    ...


def vista_complete_rad_exam(
    patient_dfn: int,
    exam_datetime: str,
    case_number: int,
    radiologist: int,
) -> dict:
    """Complete radiology exam. Transitions status to EXAMINED.
    Source: RAORDC (VistA Radiology)
    """
    ...


def vista_enter_rad_report(
    patient_dfn: int,
    exam_datetime: str,
    case_number: int,
    report_text: str,
) -> dict:
    """Enter radiology report text. Sets report status to DRAFT.
    Source: RART (VistA Radiology)
    """
    ...


def vista_verify_rad_report(
    patient_dfn: int,
    exam_datetime: str,
    case_number: int,
    verifying_radiologist: int,
) -> dict:
    """Verify radiology report. Sets report VERIFIED, exam COMPLETE.
    Source: RARTVER (VistA Radiology)
    """
    ...


# ── Operations: Scheduling ──────────────────────────────────

def vista_make_appointment(
    patient_dfn: int,
    clinic_ien: int,
    appointment_datetime: str,
    length_minutes: int,
    appointment_type: int,
    overbook: bool = False,
    consult_ien: Optional[int] = None,
) -> dict:
    """Book a new appointment.
    Source: SDM1A:S1, SDECAPI:MAKE (VistA Scheduling)
    """
    ...


def vista_cancel_appointment(
    patient_dfn: int,
    appointment_datetime: str,
    cancel_reason: int,
    cancel_remarks: Optional[str] = None,
) -> dict:
    """Cancel an appointment.
    Source: SDCNP0:CAN, SDECAPI:CANCEL (VistA Scheduling)
    """
    ...


def vista_checkin_appointment(patient_dfn: int, appointment_datetime: str) -> dict:
    """Check in a patient for their appointment.
    Source: SDAM2:ONE, SDECAPI:CHECKIN (VistA Scheduling)
    """
    ...


def vista_checkout_appointment(patient_dfn: int, appointment_datetime: str) -> dict:
    """Check out a patient from their appointment.
    Source: SDCO0, SDCOU, SDAUT2 (VistA Scheduling)
    """
    ...


def vista_noshow_appointment(patient_dfn: int, appointment_datetime: str) -> dict:
    """Mark an appointment as no-show.
    Source: SDN:EN1, SDN2 (VistA Scheduling)
    """
    ...


# ── Operations: TIU ────────────────────────────────────────

def vista_create_note(
    patient_dfn: int,
    document_type: int,
    author: int,
    text: str,
    visit: Optional[int] = None,
    location: Optional[int] = None,
) -> dict:
    """Create a new clinical note document.
    Source: TIUEDIT:MAIN (VistA TIU)
    """
    ...


def vista_sign_note(
    document_ien: int,
    signing_provider: int,
    electronic_signature: str,
) -> dict:
    """Sign an unsigned clinical note.
    Source: TIUSRVP2:SIGN (VistA TIU)
    """
    ...


def vista_cosign_note(
    document_ien: int,
    cosigning_provider: int,
    electronic_signature: str,
) -> dict:
    """Cosign a clinical note that requires cosignature.
    Source: TIUSRVP2:COSIGN (VistA TIU)
    """
    ...


def vista_addend_note(
    parent_document_ien: int,
    author: int,
    text: str,
) -> dict:
    """Add an addendum to a completed/signed clinical note.
    Source: TIUADD (VistA TIU)
    """
    ...


# ── Operations: Vitals ─────────────────────────────────────

def vista_enter_vitals(
    patient_dfn: int,
    vital_type: int,
    reading: str,
    datetime_taken: str,
    entered_by: int,
    hospital_location: Optional[int] = None,
    qualifiers: Optional[list] = None,
    supplemental_o2: Optional[str] = None,
) -> dict:
    """Enter a new vital sign measurement for a patient.
    Source: GMRVED0 → GMRVED1 → GMRVED2:ADDNODE (VistA Vitals)
    """
    ...


def vista_list_vitals(
    patient_dfn: int,
    vital_type_filter: Optional[int] = None,
    include_errors: bool = False,
) -> dict:
    """List vital sign measurements for a patient.
    Source: GMRVDS0/GMRVDS1 (VistA Vitals)
    """
    ...


def vista_mark_vitals_error(
    vital_ien: int,
    error_reason: int,
    marked_by: int,
) -> dict:
    """Mark a vital measurement as entered-in-error.
    Source: GMRVEE1:ERREN (VistA Vitals)
    """
    ...
