from datetime import datetime, timedelta, UTC
from hashlib import sha256
import secrets
from uuid import UUID

from app.modules.identity.invitation_models import UserInvitation
from app.modules.identity.repository import IdentityRepository
from app.core.security.hashing import hash_password
from app.modules.identity.enums import AccountStatus
from app.modules.identity.exceptions import (
    ExpiredInvitationError,
    InvalidInvitationError,
    InvitationAlreadyUsedError,
)


class InvitationService:
    """
    Service responsible for creating and validating user invitations.

    Raw invitation tokens are never persisted.
    """

    INVITATION_TTL_HOURS = 48

    def __init__(
        self,
        repository: IdentityRepository,
    ) -> None:
        self.repository = repository

    @staticmethod
    def _hash_token(token: str) -> str:
        """
        Hash an invitation token before persistence.
        """

        return sha256(
            token.encode("utf-8"),
        ).hexdigest()

    def create_invitation(
        self,
        *,
        hospital_id: UUID,
        user_id: UUID,
    ) -> tuple[str, datetime]:
        """
        Create a new invitation for a user.

        Returns
        -------
        str
            The raw one-time token.

        Security
        --------
        Only the hash is persisted.
        """

        raw_token = secrets.token_urlsafe(48)

        token_hash = self._hash_token(
            raw_token,
        )

        expires_at = (
            datetime.now(UTC)
            + timedelta(
                hours=self.INVITATION_TTL_HOURS,
            )
        )

        invitation = UserInvitation(
            hospital_id=hospital_id,
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        self.repository.create_invitation(
            invitation,
        )

        self.repository.flush()

        return raw_token, expires_at

    def activate_user(
        self,
        *,
        token: str,
        password: str,
    ) -> UserInvitation:
        """
        Activate a pending user using a valid invitation token.

        The invitation must:
        - exist,
        - not have been used,
        - not be expired,
        - belong to a pending user.

        The supplied password becomes the user's new password.

        Does NOT commit.
        """

        token_hash = self._hash_token(token)

        invitation = (
            self.repository.get_invitation_by_token_hash(
                token_hash,
            )
        )

        if invitation is None:
            raise InvalidInvitationError(
                "Invalid invitation.",
            )

        now = datetime.now(UTC)

        if invitation.used_at is not None:
            raise InvitationAlreadyUsedError(
                "Invitation has already been used.",
            )

        if invitation.expires_at <= now:
            raise ExpiredInvitationError(
                "Invitation has expired.",
            )

        user = self.repository.get_user_by_id(
            invitation.user_id,
        )

        if user is None:
            raise ValueError(
                "Invitation user no longer exists.",
            )

        if user.status != AccountStatus.PENDING:
            raise ValueError(
                "User account is not pending activation.",
            )

        user.password_hash = hash_password(
            password,
        )

        user.password_changed_at = now
        user.status = AccountStatus.ACTIVE

        self.repository.mark_invitation_used(
            invitation,
            used_at=now,
        )

        return invitation