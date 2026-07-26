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
    )

    # Collection of role assignments for this user.
    #
    # A user may hold multiple roles simultaneously.
    user_roles = relationship(
        "UserRole",
        back_populates="user_account",
        foreign_keys="UserRole.user_account_id",
        cascade="all, delete-orphan",
    )

    staff_profile: Mapped["Staff | None"] = relationship(
        back_populates="user_account",
        uselist=False,
    )



class Role(BaseEntity):
    """
    Represents a collection of permissions.

    Roles simplify authorization by grouping related permissions
    together.

    Instead of assigning individual permissions directly to users,
    LIGHTBURGH assigns roles.

    Examples
    --------
    - Doctor
    - Nurse
    - Pharmacist
    - Receptionist
    - Medical Director
    - Laboratory Manager

    Architectural Notes
    -------------------
    Roles belong to individual hospitals (tenants).

    A hospital may create its own custom roles in addition to
    LIGHTBURGH system roles.

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
#
# Prevents duplicate role names within the same hospital.
#
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
    # Example:
    # "Doctor"
    # "Receptionist"
    # "Medical Director"
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Optional description explaining the purpose of the role.
    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Indicates whether this role is provided by the
    # LIGHTBURGH platform itself.
    #
    # System roles should generally not be modified by
    # hospital administrators.
    is_system_role: Mapped[bool] = mapped_column(
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
    )

    # Users assigned to this role.
    #
    # The relationship returns UserRole entities rather than
    # UserAccount objects because UserRole represents the
    # assignment event itself.
    user_roles = relationship(
        "UserRole",
        back_populates="role",
        cascade="all, delete-orphan",
    )

    # Collection of permission assignments for this role.
    # NOTE:
    # This relationship returns RolePermission entities rather
    # than Permission entities because the assignment itself
    # is modeled as a first-class business object.
    role_permissions = relationship(
        "RolePermission",
        back_populates="role",
        cascade="all, delete-orphan",
        )



class Permission(BaseEntity):
    """
    Represents a single system capability within LIGHTBURGH.

    Permissions are the smallest unit of authorization.

    They are assigned to Roles through the RolePermission entity.
    User accounts inherit permissions through their assigned roles.

    Examples
    --------
    patient.read

    patient.create

    patient.update

    laboratory.verify_result

    theatre.schedule.create

    billing.invoice.approve

    Architectural Notes
    -------------------
    Permissions are global across the LIGHTBURGH platform.

    Hospitals do not authenticate against permissions directly.

    Instead:

        User
            ↓
        Role
            ↓
        Permission

    This greatly simplifies authorization management.
    """

    # ------------------------------------------------------------------
    # Database Configuration
    # ------------------------------------------------------------------

    __tablename__ = "permissions"

    # ------------------------------------------------------------------
    # Columns
    # ------------------------------------------------------------------

    # Machine-readable permission code.
    #
    # Examples:
    #
    # patient.read
    # patient.update
    # laboratory.verify
    code: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        unique=True,
        index=True,
    )

    # Human-readable permission name.
    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    # Optional explanation of the permission.
    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Functional module that owns this permission.
    #
    # Examples:
    # Identity
    # Patients
    # Laboratory
    # Billing
    module: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Indicates whether this permission is provided by
    # the LIGHTBURGH platform.
    #
    # System permissions cannot normally be deleted.
    is_system_permission: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    # Role assignments that include this permission.
    role_permissions = relationship(
        "RolePermission",
        back_populates="permission",
        cascade="all, delete-orphan",
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
    )

    # Administrator who granted the role.
    assigned_by = relationship(
        "UserAccount",
        foreign_keys=[assigned_by_user_id],
    )


class RolePermission(BaseEntity):
    """
    Represents the assignment of a Permission to a Role.

    Rather than using a simple many-to-many table,
    LIGHTBURGH models this relationship as an explicit
    entity.

    This provides flexibility for future enhancements such as:

    - Permission auditing
    - Approval workflows
    - Expiring permissions
    - Delegated administration

    Architectural Notes
    -------------------
    A Role may contain many permissions.

    A Permission may belong to many roles.

    This entity represents the assignment itself.
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

    # Permission assigned to the role.
    permission_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    # Role that owns this permission assignment.
    role = relationship(
        "Role",
        back_populates="role_permissions",
    )

    # Permission included in the role.
    permission = relationship(
        "Permission",
        back_populates="role_permissions",
    )