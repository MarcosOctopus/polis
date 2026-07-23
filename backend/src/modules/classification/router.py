"""Classification router — endpoints for IA classification of messages."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Tenant
from src.database.models_extensions import MessageClassification
from src.modules.auth.dependencies import get_current_tenant, get_current_user, get_db
from src.modules.classification.schemas import (
    ClassificationOut,
    ClassificationResponse,
    ClassifyRequest,
    ClassifyResponse,
    PaginatedResponse,
    ReclassifyRequest,
)
from src.modules.classification.service import ClassificationService
from src.config.settings import settings
from src.modules.classification.classifier import MessageClassifier

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/classification", tags=["Classification"])

# ── Shared classifier instance ────────────────────────────────────────────
_classifier: MessageClassifier | None = None


def _get_classifier() -> MessageClassifier:
    """Return a singleton MessageClassifier."""
    global _classifier
    if _classifier is None:
        _classifier = MessageClassifier(api_key=settings.openai_api_key)
    return _classifier


def _get_service() -> ClassificationService:
    """Return a service wired with the shared classifier."""
    return ClassificationService(classifier=_get_classifier())


# ── POST /classify ────────────────────────────────────────────────────────
@router.post("/classify", response_model=ClassifyResponse, status_code=status.HTTP_201_CREATED)
async def classify_message(
    body: ClassifyRequest,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Classify a single message using the IA pipeline."""
    service = _get_service()
    classification = await service.classify_message(
        session=db,
        tenant_id=tenant.id,
        msg_text=body.message_text,
        msg_id=body.message_id,
        contact_id=body.contact_id,
    )
    return ClassifyResponse(
        classification=ClassificationResponse.model_validate(classification)
    )


# ── GET /{message_id} ─────────────────────────────────────────────────────
@router.get("/{message_id}", response_model=ClassificationResponse)
async def get_classification(
    message_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Get the classification for a specific message."""
    service = _get_service()
    classification = await service.get_message_classification(
        session=db, msg_id=message_id, tenant_id=tenant.id
    )
    if classification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classification not found for this message",
        )
    return ClassificationResponse.model_validate(classification)


# ── GET / (list) ──────────────────────────────────────────────────────────
@router.get("", response_model=PaginatedResponse)
async def list_classifications(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    classification_type: str | None = Query(None),
    sentiment: str | None = Query(None),
    urgency: str | None = Query(None),
    risk: str | None = Query(None),
    category: str | None = Query(None),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """List classifications for the current tenant with optional filters."""
    service = _get_service()
    filter_by = {
        "classification_type": classification_type,
        "sentiment": sentiment,
        "urgency": urgency,
        "risk": risk,
        "category": category,
    }
    # Remove None values
    filter_by = {k: v for k, v in filter_by.items() if v is not None}

    rows, total = await service.get_classifications(
        session=db,
        tenant_id=tenant.id,
        limit=limit,
        offset=offset,
        filter_by=filter_by or None,
    )
    return PaginatedResponse(
        items=[ClassificationResponse.model_validate(r) for r in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


# ── PUT /{classification_id} (reclassify) ────────────────────────────────
@router.put("/{classification_id}", response_model=ClassificationResponse)
async def reclassify_classification(
    classification_id: str,
    body: ReclassifyRequest,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Manually override classification fields."""
    service = _get_service()
    classification = await service.reclassify(
        session=db,
        classification_id=classification_id,
        override_data=body,
        tenant_id=tenant.id,
    )
    if classification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classification not found",
        )
    return ClassificationResponse.model_validate(classification)
