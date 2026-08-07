# ============================================================================
# LIGHTBURGH EMR
#
# SOFTWARE ARCHITECTURE
# ============================================================================
#
# Version: 2.0
#
# ============================================================================

# Purpose

This document defines the architectural philosophy of LIGHTBURGH.

It explains how the platform is organised, how its major business domains
interact, and the principles that guide every architectural decision.

This document intentionally avoids implementation details such as frameworks,
programming languages and database technologies.

Instead, it defines how LIGHTBURGH thinks about healthcare.

---

# Architectural Vision

LIGHTBURGH is an Episode-driven Hospital Operating System.

Healthcare is represented as Episodes of Care composed of Clinical Events.

Clinical Events become the foundation upon which documentation, billing,
analytics, auditing, reporting and operational workflows are built.

Every module contributes to the same patient journey rather than operating as
an isolated system.

---

# Architectural Goals

Every architectural decision should improve one or more of the following:

- Simplicity
- Modularity
- Security
- Maintainability
- Extensibility
- Testability
- Scalability

Complexity should only be introduced when it delivers measurable value.

---

# Core Architectural Principles

## 1. Business Before Technology

Technology exists to support healthcare delivery.

Business workflows define the architecture—not programming frameworks.

---

## 2. Patient-Centred Design

Every workflow ultimately exists to improve patient care.

Departments do not own patients.

Departments collaborate around Episodes of Care.

---

## 3. Episode-driven Healthcare

Healthcare is organised around Episodes of Care rather than isolated visits.

Examples include:

- Pregnancy
- Stroke Admission
- Diabetes Follow-up
- Trauma Admission
- Hypertension Management

Each Episode represents one continuous healthcare journey.

---

## 4. Clinical Events are Business Facts

Every meaningful activity performed during patient care becomes a Clinical
Event.

Examples include:

- Patient Registered
- Consultation Completed
- Investigation Ordered
- Sample Collected
- Result Verified
- Diagnosis Recorded
- Prescription Created
- Medication Dispensed
- Patient Admitted
- Patient Discharged

Clinical Events describe what happened.

They do not describe pricing.

They do not describe invoices.

They do not describe business policy.

---

## 5. Business Policies Consume Clinical Events

Clinical Events record business facts.

Business Policies determine how hospitals respond to those facts.

Examples include:

- Should this Event generate a charge?
- Is supervisor approval required?
- Should a notification be sent?
- Should this Event appear in management reports?

This separation allows hospitals to customise operational behaviour without
changing clinical workflows.

---

## 6. Workspace-oriented User Experience

Users work within role-specific Workspaces rather than individual business
modules.

Examples include:

- Reception Workspace
- Clinic Workspace
- Emergency Workspace
- Ward Workspace
- Theatre Workspace
- Laboratory Workspace
- Radiology Workspace
- Pharmacy Workspace
- Billing Workspace
- Administration Workspace

Each Workspace combines functionality from multiple business domains.

---

## 7. Modular Business Domains

Each business capability is implemented as an independent domain.

Examples include:

- Identity
- Patient
- Laboratory
- Radiology
- Pharmacy
- Theatre
- Billing
- Inventory
- Reporting

Domains communicate through well-defined interfaces while remaining
independently maintainable.

---

# High-Level Architecture

```
Users
    │
    ▼
Workspaces
    │
    ▼
Business Domains
    │
    ▼
Shared Platform Services
    │
    ▼
Data Persistence
```

---

# Core Business Model

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

Every clinical module contributes Clinical Events to the same Episode.

---

# Identity Architecture

Identity is responsible for authentication and authorization across the
platform.

LIGHTBURGH separates platform capabilities from hospital responsibilities.

## Platform Responsibilities

The platform owns Permissions.

Permissions define immutable platform capabilities such as:

- patient.read
- patient.create
- laboratory.verify_result
- pharmacy.dispense
- billing.create_invoice

Hospitals cannot create arbitrary platform permissions.

---

## Hospital Responsibilities

Hospitals own Roles.

Roles represent local job functions such as:

- Doctor
- Consultant
- Nurse
- Laboratory Scientist
- Pharmacist
- Cashier

Hospitals determine which Permissions belong to each Role.

This separation enables local flexibility while maintaining platform
consistency.

---

# Billing Architecture

Billing is not a standalone workflow.

Billing consumes Clinical Events.

```
Clinical Event
        │
        ▼
Business Policy
        │
        ▼
Pricing Catalogue
        │
        ▼
Charge
        │
        ▼
Invoice
```

Hospitals decide which Clinical Events are billable.

Different hospitals may implement different charging policies while using the
same clinical workflows.

---

# Consumers of Clinical Events

Clinical Events become the single source of truth for multiple platform
capabilities.

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

---

# Shared Platform Services

Business domains share reusable platform capabilities including:

- Authentication
- Authorization
- Notifications
- File Storage
- Search
- Configuration
- Scheduling
- Audit Logging

These services remain independent of individual clinical domains.

---

# Security Principles

Every request must satisfy three conditions:

- Authenticated
- Authorised
- Scoped to a Hospital

The platform follows the Principle of Least Privilege.

Every user should only access the information required for their role.

---

# Auditability

Clinical Events and Audit Logs serve different purposes.

Clinical Events describe healthcare.

Audit Logs describe system activity.

Both are essential and should remain independent.

---

# Deployment Architecture

LIGHTBURGH is implemented as a Modular Monolith.

Business domains remain independent within a single deployable application.

This approach provides:

- Faster development
- Simpler deployment
- Strong domain boundaries

The architecture supports future decomposition into microservices if justified
by business requirements.

---

# Future Evolution

The architecture supports future capabilities including:

- Telemedicine
- Mobile Applications
- Patient Portal
- AI-assisted Clinical Decision Support
- HL7 / FHIR Integration
- Population Health Analytics
- Public Health Reporting

These capabilities should integrate by consuming Clinical Events rather than
creating isolated workflows.

---

# Guiding Principle

Healthcare is represented as Episodes of Care composed of Clinical Events.

Clinical Events are immutable business facts.

Business Policies determine how hospitals respond to those facts.

Everything else—including billing, reporting, analytics, auditing,
notifications and AI—is derived from Clinical Events.