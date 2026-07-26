"""
==============================================================================
LIGHTBURGH EMR

Base API Schemas

==============================================================================

Purpose
-------
Defines the common Pydantic base class used throughout the application.

All request and response schemas should inherit from BaseSchema to ensure
consistent configuration across every module.

Responsibilities
----------------
• Provide a common base for all API schemas.
• Enable construction from SQLAlchemy ORM objects.
• Centralize shared Pydantic configuration.

Architecture
------------
HTTP Request
      │
      ▼
Module Schema
      │
      ▼
BaseSchema
      │
      ▼
Pydantic

Notes
-----
This module should remain lightweight.

Business rules belong to the Service layer.

Database definitions belong to SQLAlchemy models.

==============================================================================
"""

from datetime import UTC, datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")

class BaseSchema(BaseModel):
    """
    Base class for all API schemas.

    Enables automatic conversion from SQLAlchemy ORM objects while
    providing a single place for future shared configuration.
    """

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
        validate_assignment=True,
        populate_by_name=True,
    )

class ErrorDetail(BaseSchema):
        """
        Represents a standardized application error.

        Attributes
        ----------
        code:
            Machine-readable application error code.

        message:
            Human-readable explanation of the error.
        """

        code: str
        message: str


class ErrorResponse(BaseSchema):
        """
        Standard response returned whenever a request fails.

        This schema provides a consistent error contract across the
        entire LIGHTBURGH API. Clients can rely on this structure
        regardless of which endpoint generated the error.

        Attributes
        ----------
        success:
            Indicates whether the request was successful.

        error:
            Details describing the application error.

        trace_id:
            Unique identifier used to correlate requests with
            application logs.

        path:
            The API endpoint that generated the error.

        timestamp:
            UTC timestamp indicating when the error occurred.
        """

        success: bool = False

        error: ErrorDetail

        trace_id: UUID

        path: str

        timestamp: datetime = Field(
            default_factory=lambda: datetime.now(UTC)
        )

class Meta(BaseSchema):
        """
        Optional metadata included in successful API responses.

        This schema provides a standard location for supplementary
        response information without affecting the primary data.

        Examples
        --------
        - Pagination information
        - Total records
        - Processing time
        - API version
        - Warnings
        """

        total: int | None = None

        page: int | None = None

        page_size: int | None = None

        processing_time_ms: float | None = None


    
class SuccessResponse(BaseSchema, Generic[T]):
    """
    Standard response returned whenever a request succeeds.

    Every successful endpoint within LIGHTBURGH should return
    this schema.

    Attributes
    ----------
    success:
        Indicates that the request completed successfully.

    data:
        The primary resource returned by the API.

    meta:
        Optional metadata associated with the response.
    """

    success: bool = True

    data: T

    meta: Meta | None = None