"""
========================================================================

LIGHTBURGH EMR

Password Hashing Utilities

========================================================================

Purpose
-------

This module centralizes all password hashing operations used throughout
the LIGHTBURGH platform.

The rest of the application should NEVER directly use the underlying
hashing library. Instead, all password-related operations should pass
through this module.

Responsibilities
----------------
- Hash new passwords
- Verify user passwords
- Determine whether stored hashes should be upgraded

Why centralize this?
--------------------
If LIGHTBURGH ever changes its hashing algorithm or security policy,
only this file needs to change. The remainder of the application
continues to work without modification.

Security Notes
--------------
- Plain-text passwords must NEVER be stored.
- Plain-text passwords must NEVER be logged.
- Password verification should always use the secure verification
  methods provided by the hashing library.
- LIGHTBURGH uses Argon2 via pwdlib, which is considered one of the
  strongest password hashing algorithms currently available.

========================================================================
"""

from pwdlib import PasswordHash

# ----------------------------------------------------------------------
# Password Hasher
# ----------------------------------------------------------------------
#
# Create a single reusable password hasher instance.
# pwdlib automatically uses secure defaults (Argon2).
#
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Convert a plain-text password into a secure Argon2 hash.

    Parameters
    ----------
    password : str
        The user's plain-text password.

    Returns
    -------
    str
        Secure hashed password suitable for database storage.
    """

    return password_hash.hash(password)


def verify_password(password: str, password_hash_from_db: str) -> bool:
    """
    Verify whether a supplied password matches the stored password hash.

    Parameters
    ----------
    password : str
        Password entered by the user.

    password_hash_from_db : str
        Previously stored password hash.

    Returns
    -------
    bool
        True if the password is correct.
        False otherwise.
    """

    return password_hash.verify(
        password,
        password_hash_from_db,
    )


def password_needs_rehash(password_hash_from_db: str) -> bool:
    """
    Determine whether a stored password hash should be upgraded.

    As password hashing recommendations evolve over time, older hashes
    may no longer meet current security standards.

    LIGHTBURGH can transparently upgrade hashes after a successful login
    without requiring the user to reset their password.

    Parameters
    ----------
    password_hash_from_db : str
        Existing stored password hash.

    Returns
    -------
    bool
        True if the password should be rehashed.
    """

    return password_hash.needs_rehash(password_hash_from_db)