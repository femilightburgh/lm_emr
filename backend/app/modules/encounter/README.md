# LIGHTBURGH EMR

# Encounter Module Directive

===============================================================================

## Purpose

The Encounter module records professional attendance to patients during
Episodes of Care.

An Encounter represents one professional's attendance to a patient within
an Episode of Care.

The Encounter is the parent context for Clinical Events.

===============================================================================

## Clinical Hierarchy

The clinical record follows this hierarchy:

    Hospital
        |
        v
    Patient
        |
        v
    Episode
        |
        v
    Encounter
        |
        v
    Event

Each level answers a different clinical question.

### Patient

Identifies the person receiving healthcare.

### Episode

Represents a single clinical visit to the hospital.

An Episode is the root container for the clinical activity occurring during
that hospital visit.

### Encounter

Represents one professional's attendance to the patient during an Episode.

Examples include:

- Doctor ward round
- Doctor consultation
- Nurse medication administration
- Nurse wound care
- Support worker personal care

The Encounter identifies the professional and the purpose of the attendance.

### Event

Represents something that happened during an Encounter.

Examples include:

- Wound dressing performed
- Laboratory result reviewed
- Investigation ordered
- Medication administered
- Clinical observation recorded
- Clinical documentation completed

Events will be implemented separately.

===============================================================================

## Core Relationships

Every Encounter:

- Belongs to exactly one Episode.
- Belongs to exactly one Staff member.
- Exists within the Hospital context of its Episode.
- Represents one professional attendance.
- May contain multiple Clinical Events.

The Encounter must not exist independently of an Episode.

The Encounter must not exist independently of the Staff member who performed
the attendance.

===============================================================================

## Encounter Identity

An Encounter is identified by:

- Encounter ID
- Episode
- Staff member
- Title
- Lifecycle status
- Start time
- End time

The title describes the purpose or nature of the professional attendance.

Examples:

    "Ward Round"
    "Medical Consultation"
    "Medication Administration"
    "Wound Care"
    "Personal Care"

The title should describe the attendance rather than individual clinical
activities performed during it.

===============================================================================

## Encounter Lifecycle

An Encounter has two lifecycle states:

    OPEN
      |
      v
    CLOSED

A newly created Encounter starts in the OPEN state.

When the professional finishes attending to the patient, the Encounter is
closed and an end timestamp is recorded.

A CLOSED Encounter represents historical professional activity.

===============================================================================

## Episode Dependency

An Encounter may only be created while its Episode is OPEN.

Encounters must not be created against:

- CLOSED Episodes
- CANCELLED Episodes

Closing an Episode establishes that no new professional attendance should
begin within that Episode.

The rules governing whether all Encounters must be closed before an Episode
can itself be closed must be explicitly enforced by the Episode/Encounter
service design.

===============================================================================

## Staff Relationship

The Encounter belongs to a Staff member, not directly to a UserAccount.

Staff represents the healthcare professional.

UserAccount represents authentication and access to the EMR.

Authentication identifies the authenticated user.

The Staff relationship identifies the professional who performed the
Encounter.

===============================================================================

## Clinical Activity Boundary

Clinical activities do not belong directly to the Encounter.

They belong to Events.

Therefore:

    Episode
        |
        +-- Encounter
        |     |
        |     +-- Event
        |     +-- Event
        |     +-- Event
        |
        +-- Encounter
              |
              +-- Event
              +-- Event

This separation allows LIGHTBURGH to distinguish:

- why the patient is at the hospital,
- who attended the patient,
- and exactly what happened during that attendance.

===============================================================================

## Auditability

Encounter records represent actual professional attendance and therefore
form part of the patient's clinical history.

The system must preserve:

- the Episode associated with the Encounter,
- the Staff member responsible for the Encounter,
- when the Encounter started,
- when the Encounter ended,
- the purpose of the Encounter,
- and the Encounter lifecycle state.

Historical Encounters must not be silently rewritten in a manner that
destroys the clinical audit trail.

===============================================================================

## Tenant Isolation

Encounters inherit Hospital ownership through their Episode.

All Encounter operations must respect the authenticated Hospital context.

A professional must not be able to access or create an Encounter belonging
to an Episode outside the authenticated Hospital.

===============================================================================

## Authorization

Encounter operations are protected by platform authorization.

The exact permission codes will be defined during implementation.

At minimum, the design must distinguish between:

- viewing Encounters,
- starting Encounters,
- closing Encounters.

Authorization must not replace business-rule validation.

The service remains responsible for validating Episode state, Staff
relationship, and Encounter lifecycle rules.

===============================================================================

## Service Boundary

Business rules belong in EncounterService.

Database access belongs in EncounterRepository.

HTTP concerns belong in the Encounter router.

Schemas define API contracts.

Models define persistence structure.

Exceptions communicate business failures.

The module must follow the same layered architecture established elsewhere
in LIGHTBURGH EMR.

===============================================================================

## Future Clinical Events

The Encounter module reserves the relationship:

    Encounter
        |
        v
    Clinical Events

The Event module will be designed separately.

The Event model must preserve its relationship to the Encounter so that every
clinical activity can ultimately be traced through:

    Event
        |
        v
    Encounter
        |
        v
    Episode
        |
        v
    Patient
        |
        v
    Hospital

This hierarchy is fundamental to clinical history, auditability, reporting,
billing, discharge documentation, and future clinical intelligence.

===============================================================================

## Design Principle

Encounter records attendance.

Event records activity.

Episode records the hospital visit.

Patient records the person.

These boundaries must remain distinct throughout implementation.

===============================================================================
