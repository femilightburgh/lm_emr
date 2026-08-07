# Patient Service

## Purpose

The Patient Service contains all business rules related to patient
management.

It sits between the API layer and the Repository layer.

---

## Responsibilities

- Register patients
- Retrieve patients
- Update patient demographics
- Prevent duplicate hospital numbers
- Raise business exceptions

---

## Does NOT

- Execute SQL
- Handle HTTP routing
- Define database models

---

## Future Responsibilities

- Validate NHIA numbers
- Validate National ID
- Patient merge
- Patient de-duplication
- Audit logging
- Event publishing