"""Template service — CRUD + rendering with variable substitution."""

import logging
import re
from typing import Dict, List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models_extensions import MessageTemplate
from src.modules.templates.schemas import (
    TemplateCreate,
    TemplateRenderResponse,
    TemplateUpdate,
)

logger = logging.getLogger(__name__)

VARIABLE_PATTERN = re.compile(r"\{\{(\w+)\}\}")


class TemplateService:
    """Business logic for message template management."""

    @staticmethod
    def _render_text(template: str, variables: Dict[str, str]) -> str:
        """Replace {{var}} placeholders with provided values."""
        def _replacer(match: re.Match) -> str:
            var_name = match.group(1)
            return variables.get(var_name, match.group(0))
        return VARIABLE_PATTERN.sub(_replacer, template)

    @staticmethod
    async def create(
        db: AsyncSession, tenant_id: str, user_id: str, data: TemplateCreate
    ) -> MessageTemplate:
        template = MessageTemplate(
            tenant_id=tenant_id,
            name=data.name,
            channel=data.channel,
            message_type=data.message_type,
            subject=data.subject,
            body=data.body,
            variables=data.variables,
            category=data.category,
            tone=data.tone,
            is_active=True,
            created_by=user_id,
        )
        db.add(template)
        await db.flush()
        await db.refresh(template)
        logger.info("Template created: %s (tenant=%s)", template.id, tenant_id)
        return template

    @staticmethod
    async def get(
        db: AsyncSession, template_id: str, tenant_id: Optional[str] = None
    ) -> Optional[MessageTemplate]:
        query = select(MessageTemplate).where(MessageTemplate.id == template_id)
        if tenant_id:
            query = query.where(MessageTemplate.tenant_id == tenant_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def list(
        db: AsyncSession,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        channel: Optional[str] = None,
    ) -> Tuple[List[MessageTemplate], int]:
        query = select(MessageTemplate).where(
            MessageTemplate.tenant_id == tenant_id,
        )
        if channel:
            query = query.where(MessageTemplate.channel == channel)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(MessageTemplate.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        templates = list(result.scalars().all())
        return templates, total

    @staticmethod
    async def update(
        db: AsyncSession,
        template_id: str,
        data: TemplateUpdate,
        tenant_id: Optional[str] = None,
    ) -> Optional[MessageTemplate]:
        template = await TemplateService.get(db, template_id, tenant_id)
        if template is None:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(template, key, value)
        await db.flush()
        await db.refresh(template)
        logger.info("Template updated: %s", template_id)
        return template

    @staticmethod
    async def delete(
        db: AsyncSession, template_id: str, tenant_id: Optional[str] = None
    ) -> bool:
        template = await TemplateService.get(db, template_id, tenant_id)
        if template is None:
            return False
        await db.delete(template)
        await db.flush()
        logger.info("Template deleted: %s", template_id)
        return True

    @staticmethod
    async def render(
        db: AsyncSession,
        template_id: str,
        variables: Dict[str, str],
        tenant_id: Optional[str] = None,
    ) -> Optional[TemplateRenderResponse]:
        template = await TemplateService.get(db, template_id, tenant_id)
        if template is None:
            return None
        rendered_body = TemplateService._render_text(template.body, variables)
        rendered_subject = None
        if template.subject:
            rendered_subject = TemplateService._render_text(template.subject, variables)
        return TemplateRenderResponse(
            rendered_body=rendered_body,
            rendered_subject=rendered_subject,
        )
