"""Pydantic schemas for the classification module."""

from datetime import datetime

from pydantic import BaseModel, Field


class ClassificationOut(BaseModel):
    """All fields from MessageClassification model."""

    id: str
    tenant_id: str
    message_id: str
    classification_type: str
    category: str | None = None
    subcategory: str | None = None
    sentiment: str | None = None
    sentiment_score: float | None = None
    urgency: str | None = None
    risk: str | None = None
    extracted_address: str | None = None
    extracted_neighborhood: str | None = None
    extracted_city: str | None = None
    extracted_state: str | None = None
    reference_point: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    geocode_source: str | None = None
    suggested_department: str | None = None
    summary: str | None = None
    keywords: list[str] | None = None
    confidence: float | None = None
    model: str | None = None
    raw_classification: dict | None = None
    territorial_event_id: str | None = None
    processed_at: datetime | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class ClassificationResponse(BaseModel):
    """Compact response for the classification router."""

    id: str
    message_id: str
    classification_type: str
    category: str | None = None
    sentiment: str | None = None
    urgency: str | None = None
    risk: str | None = None
    confidence: float | None = None
    summary: str | None = None
    suggested_department: str | None = None
    keywords: list[str] | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class ClassifyRequest(BaseModel):
    """Request to classify a single message."""

    message_text: str = Field(..., min_length=1, max_length=10000)
    message_id: str = Field(..., min_length=1)
    contact_id: str | None = None


class BatchClassifyRequest(BaseModel):
    """Batch classification request."""

    tenant_id: str = Field(..., min_length=1)
    messages: list[ClassifyRequest] = Field(..., min_length=1, max_length=100)


class ClassifyResponse(BaseModel):
    """Response from a classify operation."""

    classification: ClassificationResponse


class ReclassifyRequest(BaseModel):
    """Override fields for manual reclassification."""

    classification_type: str | None = None
    category: str | None = None
    subcategory: str | None = None
    sentiment: str | None = None
    sentiment_score: float | None = None
    urgency: str | None = None
    risk: str | None = None
    extracted_address: str | None = None
    extracted_neighborhood: str | None = None
    extracted_city: str | None = None
    extracted_state: str | None = None
    reference_point: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    geocode_source: str | None = None
    suggested_department: str | None = None
    summary: str | None = None
    keywords: list[str] | None = None
    confidence: float | None = None
    territorial_event_id: str | None = None


class PaginatedResponse(BaseModel):
    """Paginated list of classifications."""

    items: list[ClassificationResponse]
    total: int
    limit: int
    offset: int
