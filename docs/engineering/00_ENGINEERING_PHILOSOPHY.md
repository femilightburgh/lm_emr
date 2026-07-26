# LIGHTBURGH EMR

# Engineering Philosophy

**Document ID:** 00_ENGINEERING_PHILOSOPHY

**Version:** 1.0

**Status:** Approved

---

# Purpose

This document defines the engineering philosophy that guides the
development of the LIGHTBURGH Electronic Medical Record (EMR) system.

It establishes the principles behind every technical decision made within
the project.

This document is intentionally independent of any programming language,
framework, or database technology. It describes *how we think* about
software engineering rather than *how we implement* software.

All engineering standards within LIGHTBURGH should align with the
principles described in this document.

Technology evolves.

Engineering principles endure.

---

# Mission

LIGHTBURGH exists to build healthcare software that is:

- Reliable
- Maintainable
- Secure
- Understandable
- Extensible

Our objective is not simply to build software that works.

Our objective is to build software that healthcare professionals can
depend upon every day for many years.

---

# Engineering Values

Every engineering decision should be evaluated against the following
values.

When multiple solutions are technically correct, the solution that best
aligns with these values should be preferred.

---

# Principle 1

## Software is Read More Than It Is Written

Software spends significantly more time being read than being written.

Code is reviewed.

Code is debugged.

Code is maintained.

Code is extended.

Code is eventually rewritten.

For this reason, readability is considered one of the highest priorities
within the LIGHTBURGH project.

Readable code reduces maintenance costs, improves collaboration, and
helps prevent defects.

A solution that is easier to understand should generally be preferred
over one that is merely shorter.

---

# Principle 2

## Code Should Describe the Business

LIGHTBURGH is a healthcare information system.

Its code should describe healthcare operations rather than technical
operations.

Whenever possible, business terminology should be preferred over
implementation terminology.

Examples include:

- Register Staff
- Admit Patient
- Record Vital Signs
- Dispense Medication
- Schedule Appointment

rather than:

- Insert Record
- Update Table
- Execute Operation
- Process Object

The code should reflect how hospitals operate.

Every service should read like a hospital workflow.

---

# Principle 3

## Explicit is Better Than Implicit

Software should make its behaviour obvious.

Hidden behaviour, unnecessary abstraction, and excessive framework magic
make software more difficult to understand and maintain.

LIGHTBURGH favours explicit implementations.

A developer should be able to understand what a function does by reading
its implementation.

Code should communicate its intent clearly.

---

# Principle 4

## Separation of Responsibilities

Each component within the system should have one primary responsibility.

Responsibilities should remain clearly separated.

Examples include:

- Models describe data.
- Schemas validate data.
- Services implement business rules.
- Routers expose HTTP endpoints.
- Exceptions describe business failures.

No component should assume responsibilities that belong to another layer.

This separation improves maintainability, testing, and long-term
extensibility.

---

# Principle 5

## Consistency Over Personal Preference

Many engineering problems have multiple valid solutions.

LIGHTBURGH values consistency more highly than individual coding style.

Once an engineering standard has been adopted, it should be applied
consistently throughout the project.

Consistency reduces cognitive load and makes the codebase easier to
understand.

The goal is not to determine whose style is best.

The goal is for the project to feel like it was built by one engineering
team.

---

# Principle 6

## Design for Growth

Healthcare systems evolve continuously.

Engineering decisions should anticipate future growth while avoiding
unnecessary complexity.

Software should be designed so that new functionality can be introduced
without requiring significant redesign.

Every design decision should consider maintainability beyond the initial
implementation.

---

# Principle 7

## Documentation is Part of the Product

Documentation is not optional.

Documentation is part of the software itself.

Every significant component should clearly explain:

- Why it exists.
- What it is responsible for.
- How it should be used.
- How it fits within the overall architecture.

Well-written documentation improves collaboration, onboarding, and
long-term maintenance.

---

# Principle 8

## Optimize for Future Developers

Every developer eventually becomes a future maintainer.

Code should therefore be written with future developers in mind.

That future developer may be:

- A teammate.
- A new contributor.
- Your future self.

Software should optimize for clarity, consistency, and maintainability.

Future developers should be able to understand the system without
guessing the author's intentions.

---

# The LIGHTBURGH Way

The LIGHTBURGH project believes that software engineering is a discipline
of communication as much as implementation.

Every class should communicate its responsibility.

Every function should communicate its intention.

Every module should communicate its place within the system.

Every architectural decision should improve the long-term health of the
project.

We value maintainability over cleverness.

We value clarity over brevity.

We value consistency over personal preference.

We build software that healthcare professionals can trust.