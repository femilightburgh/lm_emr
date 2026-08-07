# ============================================================================
# LIGHTBURGH EMR
#
# DOMAIN MODEL
# ============================================================================
#
# Purpose
# -------
#
# Defines the conceptual model of the LIGHTBURGH platform.
#
# This document describes how healthcare is represented within the system.
#
# It intentionally focuses on business concepts rather than implementation
# details or database structures.
#
# Every module, workflow and architectural decision should align with the
# principles described here.
#
# ============================================================================

# Domain Philosophy

Healthcare is not a collection of unrelated forms.

Healthcare is a continuous journey consisting of interactions between patients,
healthcare professionals, departments and hospital services.

LIGHTBURGH models this journey using Episodes of Care, Encounters and
Clinical Events.

Clinical Events represent immutable business facts that occur during patient
care. They become the foundation upon which documentation, billing,
analytics, auditing and operational workflows are built.

Instead of treating billing, laboratory, pharmacy and other modules as isolated
systems, LIGHTBURGH treats them as contributors to a single clinical story.

---

# Core Principles

## 1. The Patient is the Centre of the System

Every workflow ultimately exists to support patient care.

Patients do not belong to departments.

Departments collaborate around patients.

---

## 2. Healthcare is Organised into Episodes of Care

A patient may have many Episodes of Care.

Examples include:

- Emergency visit
- Outpatient consultation
- Hospital admission
- Surgical admission
- Antenatal care
- Chronic disease follow-up

Each Episode represents one continuous healthcare journey.

---

## 3. Episodes consist of Encounters

An Episode may contain one or more Encounters.

Examples include:

- Registration
- Nurse assessment
- Doctor consultation
- Ward review
- Theatre review
- Pharmacy counselling

Encounters organise healthcare activities into meaningful clinical interactions.

---

## 4. Encounters consist of Clinical Events

Clinical Events are the smallest meaningful units of work performed within
LIGHTBURGH.

Examples include:

- Patient registered
- Vital signs recorded
- Consultation completed
- Diagnosis recorded
- Laboratory investigation ordered
- Sample collected
- Result verified
- Prescription created
- Drug dispensed
- Admission initiated
- Procedure completed
- Patient discharged

Clinical Events represent business facts.

They describe what happened.

They are not user interface actions.

They are not invoices.

They are not reports.

---

## 5. Clinical Events are Immutable

Clinical Events should be treated as historical facts.

If a mistake occurs, another Clinical Event should record the correction rather
than rewriting history whenever practical.

This preserves a complete and auditable clinical timeline.

---

# Domain Hierarchy

```
Patient
    │
    ▼
Episode of Care
    │
    ▼
Encounter
    │
    ▼
Clinical Event
```

This hierarchy represents the fundamental structure of healthcare within
LIGHTBURGH.

---

# Consumers of Clinical Events

Clinical Events become the single source of truth for multiple parts of the
platform.

```
Clinical Event
        │
        ├────────► Clinical Documentation
        ├────────► Billing
        ├────────► Audit
        ├────────► Reporting
        ├────────► Analytics
        ├────────► Operational KPIs
        ├────────► AI Decision Support
        └────────► Future Integrations
```

Every downstream capability derives information from Clinical Events rather
than maintaining separate independent workflows.

---

# Billing Philosophy

LIGHTBURGH does not treat billing as an isolated subsystem.

Billing is derived from Clinical Events.

Each Clinical Event may be configured by hospital policy as:

- Billable
- Non-billable

Examples:

| Clinical Event | Billable |
|----------------|----------|
| Registration | Yes |
| Nurse Triage | No |
| Consultation | Yes |
| Laboratory Investigation | Yes |
| Drug Dispensing | Yes |
| Discharge | No |

Hospitals determine their own billing policies without changing clinical
workflows.

This allows different hospitals to implement different pricing strategies while
using the same platform.

---

# Identity Domain

LIGHTBURGH separates platform capabilities from hospital responsibilities.

## Platform Responsibilities

The platform owns Permissions.

Permissions describe capabilities supported by LIGHTBURGH.

Examples include:

- patient.read
- patient.create
- patient.update
- laboratory.verify_result
- pharmacy.dispense
- billing.create_invoice

Platform permissions are immutable.

Hospitals cannot create arbitrary permissions.

---

## Hospital Responsibilities

Hospitals own Roles.

Roles represent local job functions.

Examples include:

- Doctor
- Consultant
- Nurse
- Laboratory Scientist
- Pharmacist
- Cashier
- Medical Director

Hospitals may create, rename or retire Roles according to their operational
requirements.

Roles simply aggregate platform permissions.

This separation allows hospitals to customise workflows without compromising
platform consistency.

---

# Modular Healthcare

Each clinical module contributes Clinical Events to an Episode of Care.

Examples include:

Reception
- Patient Registered
- Patient Checked In

Nursing
- Vital Signs Recorded
- Triage Completed

Consultation
- Diagnosis Recorded
- Treatment Plan Created

Laboratory
- Investigation Ordered
- Sample Collected
- Result Verified

Radiology
- Imaging Ordered
- Report Completed

Pharmacy
- Prescription Dispensed

Billing
- Invoice Generated
- Payment Received

Admission
- Patient Admitted
- Patient Discharged

Every module contributes to the same patient journey.

---

# Artificial Intelligence

Artificial Intelligence is an assistant, not a decision maker.

AI consumes Clinical Events to provide:

- Guideline-based recommendations
- Clinical documentation assistance
- Operational insights
- Decision support

Final clinical responsibility always remains with qualified healthcare
professionals.

---

# Future Evolution

The Domain Model is expected to evolve as LIGHTBURGH grows.

Future modules—including Inventory, Theatre, Blood Bank, Intensive Care,
Public Health and Research—should integrate by contributing Clinical Events
rather than introducing isolated workflows.

This ensures that every part of the platform contributes to a single,
consistent representation of healthcare.

---

# Guiding Principle

Every patient journey is represented as an Episode of Care composed of
Clinical Events.

Clinical Events are the foundation upon which documentation, billing,
analytics, auditing and operational intelligence are built.

Everything else in LIGHTBURGH exists to support, enrich or consume those
Clinical Events.