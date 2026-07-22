"""Pydantic schemas for the territorial module."""

from datetime import datetime

from pydantic import BaseModel, Field


class TerritorialEventCreate(BaseModel):
    event_type: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    location: dict | None = Field(
        None,
        description="Geographic location: {'lat': -23.55, 'lng': -46.63, 'address': '...', 'city': 'SP'}",
    )
    severity: str | None = Field(None, min_length=1, max_length=20)
    occurred_at: datetime | None = None
    metadata: dict | None = None


class TerritorialEventUpdate(BaseModel):
    event_type: str | None = Field(None, min_length=1, max_length=100)
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    location: dict | None = None
    severity: str | None = None
    occurred_at: datetime | None = None
    metadata: dict | None = None


class TerritorialEventResponse(BaseModel):
    id: str
    tenant_id: str
    event_type: str
    title: str
    description: str | None = None
    location: dict | None = None
    severity: str | None = None
    occurred_at: datetime | None = None
    metadata: dict | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class TerritorialEventList(BaseModel):
    items: list[TerritorialEventResponse]
    total: int
    skip: int
    limit: int


class TerritorialMapPoint(BaseModel):
    """Lightweight geo-point for map rendering."""

    id: str
    event_type: str
    title: str
    severity: str | None = None
    location: dict | None = None
    occurred_at: datetime | None = None


class TerritorialStats(BaseModel):
    """Aggregated territorial statistics."""

    total_events: int
    by_type: dict[str, int]
    by_severity: dict[str, int]
    latest_event: TerritorialEventResponse | None = None
