# Common Module

## Purpose

The Common module contains reusable components shared across the entire LIGHTBURGH platform.

Business modules should depend on Common, but Common must never depend on any business module.

## Responsibilities

- Shared enums
- Shared constants
- Validation helpers
- Utility functions
- Custom exceptions
- Common type aliases

## Rules

- Do not place business logic here.
- Do not import business modules.
- Keep utilities generic and reusable.

## Examples

✔ Email validator

✔ Phone validator

✔ Date utilities

✔ UUID utilities

✘ Patient validation

✘ Hospital repository

✘ Appointment service