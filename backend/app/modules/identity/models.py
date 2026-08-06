"""
========================================================================

LIGHTBURGH EMR

Identity Domain Models

========================================================================

Domain Responsibility
---------------------

The Identity module is responsible for:

• Authentication identities
• Authorization
• Role assignments
• Permission management

It intentionally does NOT manage:

• Employment
• Professional qualifications
• Clinical privileges
• Staff demographics

Those belong to the Staff module.

------------------------------------------------------------------------

Entity Diagram

Hospital
    │
    ├──────────────┐
    ▼              │
UserAccount        │
    │              │
    ▼              │
UserRole──────────►Role
                     │
                     ▼
             RolePermission
                     │
                     ▼
               Permission

========================================================================
"""

from datetime import UTC, datetime

from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_entity import BaseEntity
from app.modules.identity.enums import AccountStatus
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.modules.staff.models import Staff


class UserAccount(BaseEntity):
    """
    Represents an authenticated identity within LIGHTBURGH.

    A UserAccount is responsible for authentication and authorization.
    It stores login credentials and security-related information but
    intentionally does NOT store employment or demographic details.

    Every user account belongs to exactly one hospital (tenant) and
    may be assigned one or more roles through the UserRole entity.

    Examples
    --------
    - Doctor
    - Nurse
    - Receptionist
    - Laboratory Scientist
    - Hospital Administrator

    Architectural Notes
    -------------------
    Authentication data belongs here.

    Employment information belongs to the Staff module.

    Professional qualifications belong to the Staff module.

    Clinical responsibilities are determined through Roles and
    Permissions rather than by profession.
    """

    # ------------------------------------------------------------------
    # Database Configuration
    # ------------------------------------------------------------------

    __tablename__ = "user_accounts"

    # ------------------------------------------------------------------
    # Database Constraints
    # ------------------------------------------------------------------
    #
    # Ensures that a user's email address is unique within a hospital.
    #
    # LIGHTBURGH is a multi-tenant platform, so two different hospitals
    # may have users with the same email address. However, a single
    # hospital cannot have duplicate email addresses.
    #
    __table_args__ = (
    UniqueConstraint(
        "hospital_id",
        "email",
        name="uq_user_account_hospital_email",
        ),
    )

    # ------------------------------------------------------------------
    # Columns
    # ------------------------------------------------------------------

    # Hospital (tenant) that owns this user account.
    hospital_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("hospitals.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # User's login email.
    #
    # NOTE:
    # Email uniqueness will later be enforced together with
    # hospital_id, allowing different hospitals to have users
    # with the same email address.
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Securely hashed password.
    #
    # Plain-text passwords must NEVER be stored.
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Current account status.
    #
    # Example values:
    # - Pending
    # - Active
    # - Suspended
    # - Locked
    status: Mapped[AccountStatus] = mapped_column(
        Enum(AccountStatus, name="account_status_enum"),
        nullable=False,
        default=AccountStatus.PENDING,
    )

    # Number of consecutive failed login attempts.
    #
    # Used to implement automatic account lockout.
    failed_login_attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # Grants unrestricted platform access.
    #
    # This should only be used for LIGHTBURGH platform
    # administrators and should be assigned sparingly.
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Timestamp of the user's most recent successful login.
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Timestamp of the most recent password change.
    #
    # This supports future password expiry policies.
    password_changed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    # Hospital (tenant) that owns this account.
    hospital = relationship(
        "Hospital",
        back_populates="user_accounts",
        lazy="selectin",
    )

    # Collection of role assignments for this user.
    #
    # A user may hold multiple roles simultaneously.
    user_roles = relationship(
        "UserRole",
        back_populates="user_account",
        foreign_keys="UserRole.user_account_id",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    staff_profile: Mapped["Staff | None"] = relationship(
        back_populates="user_account",
        uselist=False,
        lazy="selectin",
    )



class Role(BaseEntity):
    """
    Represents a collection of permissions.

    Roles simplify authorization by grouping related permissions
    together.

    Rather than assigning permissions directly to users,
    LIGHTBURGH assigns permissions to roles.

    Hospitals are free to create, modify, rename, or delete
    roles according to their organizational structure.

    Examples
    --------
    - Consultant
    - Resident
    - Medical Officer
    - Senior Nurse
    - Ward Manager
    - Clinical Coordinator

    Architectural Notes
    -------------------
    Roles belong to individual hospitals (tenants).

    LIGHTBURGH provides optional default role templates during
    hospital onboarding, but authorization is driven entirely by
    permissions rather than role names.

    Permissions are linked through the RolePermission entity
    rather than a direct many-to-many relationship to allow
    future auditing and metadata.
    """

    # ------------------------------------------------------------------
    # Database Configuration
    # ------------------------------------------------------------------

    __tablename__ = "roles"

    # ------------------------------------------------------------------
    # Database Constraints
    # ------------------------------------------------------------------

    # Prevent duplicate role names within a hospital.
    __table_args__ = (
        UniqueConstraint(
            "hospital_id",
            "name",
            name="uq_role_hospital_name",
        ),
    )

    # ------------------------------------------------------------------
    # Columns
    # ------------------------------------------------------------------

    # Hospital that owns this role.
    hospital_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("hospitals.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Human-readable role name.
    #
    # Examples:
    # - Consultant
    # - Resident
    # - Receptionist
    # - Clinical Coordinator
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Optional description explaining the purpose of the role.
    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Indicates whether this role was created automatically by
    # LIGHTBURGH during hospital provisioning.
    #
    # Template roles serve only as starting templates.
    # Hospitals remain free to rename, modify or delete them.
    is_template: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    # Hospital that owns this role.
    hospital = relationship(
        "Hospital",
        back_populates="roles",
        lazy="selectin",
    )

    # Users assigned to this role.
    user_roles = relationship(
        "UserRole",
        back_populates="role",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Permissions assigned to this role.
    role_permissions = relationship(
        "RolePermission",
        back_populates="role",
        cascade="all, delete-orphan",
        lazy="selectin",
    )



class Permission(BaseEntity):
    """
    Represents a platform capability.

    Permissions define the actions supported by the LIGHTBURGH
    platform.

    Unlike roles, permissions are platform-owned and remain
    consistent across all hospitals.

    Hospitals grant permissions to their own custom roles to
    implement their preferred authorization model.

    Examples
    --------
    - patient.read
    - patient.create
    - patient.update
    - laboratory.request
    - billing.invoice.create

    Architectural Notes
    -------------------
    Permission codes are globally unique.

    The module can always be derived from the permission code.

    Example:
        patient.read

    Module:
        patient

    Action:
        read

    Permissions are linked to roles through the RolePermission
    entity to support future auditing and extensibility.
    """

    # ------------------------------------------------------------------
    # Database Configuration
    # ------------------------------------------------------------------

    __tablename__ = "permissions"

    # ------------------------------------------------------------------
    # Database Constraints
    # ------------------------------------------------------------------

    __table_args__ = (
        UniqueConstraint(
            "code",
            name="uq_permission_code",
        ),
    )

    # ------------------------------------------------------------------
    # Columns
    # ------------------------------------------------------------------

    # Globally unique permission code.
    #
    # Examples:
    # patient.read
    # laboratory.request
    # billing.invoice.create
    code: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    # Human-readable permission name.
    #
    # Example:
    # Read Patients
    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    # Optional description explaining the permission.
    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Indicates whether this permission is provided by
    # the LIGHTBURGH platform.
    #
    # Future marketplace plugins may introduce additional
    # permissions that are not part of the core platform.
    is_platform_permission: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    # Roles granted this permission.
    #
    # The assignment itself is represented by the
    # RolePermission entity.
    role_permissions = relationship(
        "RolePermission",
        back_populates="permission",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    


class UserRole(BaseEntity):
    """
    Represents the assignment of a Role to a UserAccount.

    Unlike a traditional many-to-many association table,
    UserRole is modeled as a first-class entity because
    role assignments are business events that may carry
    their own lifecycle and audit information.

    Examples
    --------
    Dr. Ade
        ├── Doctor
        ├── Medical Director
        └── Research Coordinator

    This design allows future support for:

    - Temporary role assignments
    - Role expiration
    - Audit trails
    - Delegated administration
    """

    # ------------------------------------------------------------------
    # Database Configuration
    # ------------------------------------------------------------------

    __tablename__ = "user_roles"

    # ------------------------------------------------------------------
    # Database Constraints
    # ------------------------------------------------------------------
    #
    # Prevents assigning the same role to the same user more than once.
    #
    __table_args__ = (
        UniqueConstraint(
            "user_account_id",
            "role_id",
            name="uq_user_role",
        ),
    )

    # ------------------------------------------------------------------
    # Columns
    # ------------------------------------------------------------------

    user_account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("user_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    assigned_by_user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("user_accounts.id"),
        nullable=True,
    )

    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    # The user who owns this role assignment.
    user_account = relationship(
        "UserAccount",
        back_populates="user_roles",
        foreign_keys=[user_account_id],
    )

    # The assigned role.
    role = relationship(
        "Role",
        back_populates="user_roles",
        lazy="selectin",
    )

    # Administrator who granted the role.
    assigned_by = relationship(
        "UserAccount",
        foreign_keys=[assigned_by_user_id],
    )


class RolePermission(BaseEntity):
    """
    Associates a role with a platform permission.

    This entity represents a permission assignment rather than
    using a direct many-to-many relationship.

    Modeling the assignment explicitly allows LIGHTBURGH to
    support future auditing, approval workflows, metadata,
    and effective-dating without redesigning the database.

    Architectural Notes
    -------------------
    A role may have many permissions.

    A permission may belong to many roles.

    Each (role, permission) pair may exist only once.
    """

    # ------------------------------------------------------------------
    # Database Configuration
    # ------------------------------------------------------------------

    __tablename__ = "role_permissions"

    # ------------------------------------------------------------------
    # Database Constraints
    # ------------------------------------------------------------------

    __table_args__ = (
        UniqueConstraint(
            "role_id",
            "permission_id",
            name="uq_role_permission",
        ),
    )

    # ------------------------------------------------------------------
    # Columns
    # ------------------------------------------------------------------

    # Role receiving the permission.
    role_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Platform permission assigned to the role.
    permission_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    # Role receiving the permission.
    role = relationship(
        "Role",
        back_populates="role_permissions",
        lazy="selectin",
    )

    # Permission granted to the role.
    permission = relationship(
        "Permission",
        back_populates="role_permissions",
        lazy="selectin",
    )
    