"""Campaign service — CRUD, send, pause, cancel, metrics."""

import logging
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Campaign, Channel, Contact, Message
from src.modules.campaigns.schemas import CampaignCreate, CampaignUpdate
from src.providers.base import MessageProvider
from src.providers.email.provider import EmailProvider
from src.providers.sms.provider import SmsProvider
from src.providers.whatsapp.provider import WhatsAppProvider

logger = logging.getLogger(__name__)


def _get_provider(channel: Channel) -> MessageProvider:
    providers = {
        "whatsapp": WhatsAppProvider,
        "email": EmailProvider,
        "sms": SmsProvider,
    }
    provider_cls = providers.get(channel.provider)
    if provider_cls is None:
        raise ValueError(f"Unknown provider: {channel.provider}")
    return provider_cls(credentials=channel.credentials, config=channel.config)


class CampaignService:
    """Business logic for campaign management."""

    @staticmethod
    async def create(
        db: AsyncSession, tenant_id: str, data: CampaignCreate
    ) -> Campaign:
        campaign = Campaign(
            tenant_id=tenant_id,
            name=data.name,
            description=data.description,
            channel_id=data.channel_id,
            segments=data.segments,
            message_template=data.message_template,
            scheduled_at=data.scheduled_at,
            metadata=data.metadata,
            status="draft" if not data.scheduled_at else "scheduled",
        )
        db.add(campaign)
        await db.flush()
        await db.refresh(campaign)
        return campaign

    @staticmethod
    async def get_by_id(
        db: AsyncSession, campaign_id: str, tenant_id: str | None = None
    ) -> Campaign | None:
        query = select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.deleted_at.is_(None),
        )
        if tenant_id:
            query = query.where(Campaign.tenant_id == tenant_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_by_tenant(
        db: AsyncSession,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
    ) -> tuple[list[Campaign], int]:
        query = select(Campaign).where(
            Campaign.tenant_id == tenant_id,
            Campaign.deleted_at.is_(None),
        )
        if status:
            query = query.where(Campaign.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(Campaign.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        campaigns = list(result.scalars().all())
        return campaigns, total

    @staticmethod
    async def update(
        db: AsyncSession,
        campaign_id: str,
        data: CampaignUpdate,
        tenant_id: str | None = None,
    ) -> Campaign | None:
        campaign = await CampaignService.get_by_id(db, campaign_id, tenant_id)
        if campaign is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(campaign, key, value)

        await db.flush()
        await db.refresh(campaign)
        return campaign

    @staticmethod
    async def soft_delete(
        db: AsyncSession, campaign_id: str, tenant_id: str | None = None
    ) -> bool:
        campaign = await CampaignService.get_by_id(db, campaign_id, tenant_id)
        if campaign is None:
            return False
        campaign.deleted_at = datetime.now(timezone.utc)
        await db.flush()
        return True

    @staticmethod
    async def send(
        db: AsyncSession, campaign_id: str, tenant_id: str | None = None
    ) -> tuple[bool, str]:
        """Send a campaign to all matching contacts."""
        campaign = await CampaignService.get_by_id(db, campaign_id, tenant_id)
        if campaign is None:
            return False, "Campaign not found"

        if campaign.status not in ("draft", "scheduled", "paused"):
            return False, f"Cannot send campaign with status '{campaign.status}'"

        if not campaign.channel_id:
            return False, "No channel configured for this campaign"

        # Get the channel
        result = await db.execute(
            select(Channel).where(
                Channel.id == campaign.channel_id,
                Channel.tenant_id == tenant_id,
                Channel.is_active == True,  # noqa: E712
            )
        )
        channel = result.scalar_one_or_none()
        if channel is None:
            return False, "Channel not found or inactive"

        # Find matching contacts based on segments
        contact_query = select(Contact).where(
            Contact.tenant_id == tenant_id,
            Contact.deleted_at.is_(None),
            Contact.is_active == True,  # noqa: E712
        )

        segments = campaign.segments or {}
        if segments.get("tags"):
            for tag in segments["tags"]:
                contact_query = contact_query.where(Contact.tags.any(tag))
        if segments.get("city"):
            contact_query = contact_query.where(Contact.city.ilike(f"%{segments['city']}%"))
        if segments.get("state"):
            contact_query = contact_query.where(Contact.state.ilike(f"%{segments['state']}%"))

        result = await db.execute(contact_query)
        contacts = list(result.scalars().all())

        if not contacts:
            return False, "No contacts match the campaign segments"

        # Update campaign status
        campaign.status = "sending"
        campaign.started_at = datetime.now(timezone.utc)
        campaign.total_contacts = len(contacts)
        await db.flush()

        # Send messages
        template = campaign.message_template or {}
        message_type = template.get("type", "text")
        text_content = template.get("text", "")
        template_name = template.get("template_name", "")
        template_params = template.get("params", {})

        sent = 0
        failed = 0

        try:
            provider = _get_provider(channel)

            for contact in contacts:
                phone = contact.phone or contact.email
                if not phone:
                    failed += 1
                    continue

                try:
                    if message_type == "text":
                        msg_status = await provider.send_text(phone, text_content)
                    elif message_type == "template":
                        msg_status = await provider.send_template(phone, template_name, template_params)
                    else:
                        msg_status = await provider.send_text(phone, text_content)

                    if msg_status.status.value in ("sent", "queued"):
                        sent += 1
                    else:
                        failed += 1

                    # Log the message in the database
                    db_message = Message(
                        tenant_id=tenant_id,
                        conversation_id="",  # Campaign messages are standalone
                        channel_id=campaign.channel_id,
                        direction="outbound",
                        message_type=message_type,
                        content={
                            "text": text_content,
                            "to": phone,
                            "campaign_id": campaign.id,
                        },
                        provider_message_id=msg_status.provider_message_id,
                        provider_status=msg_status.status.value,
                    )
                    db.add(db_message)
                except Exception as exc:
                    logger.exception("Failed to send campaign message to %s", phone)
                    failed += 1

                await db.flush()

        except Exception as exc:
            logger.exception("Campaign send error")
            campaign.status = "failed"
            campaign.sent_count = sent
            campaign.failed_count = failed
            await db.flush()
            return False, f"Provider error: {str(exc)}"

        campaign.status = "completed"
        campaign.completed_at = datetime.now(timezone.utc)
        campaign.sent_count = sent
        campaign.failed_count = failed
        await db.flush()

        return True, f"Campaign sent: {sent} delivered, {failed} failed"

    @staticmethod
    async def pause(
        db: AsyncSession, campaign_id: str, tenant_id: str | None = None
    ) -> Campaign | None:
        """Pause a sending campaign."""
        campaign = await CampaignService.get_by_id(db, campaign_id, tenant_id)
        if campaign is None:
            return None

        if campaign.status != "sending":
            return None

        campaign.status = "paused"
        await db.flush()
        await db.refresh(campaign)
        return campaign

    @staticmethod
    async def cancel(
        db: AsyncSession, campaign_id: str, tenant_id: str | None = None
    ) -> Campaign | None:
        """Cancel a campaign."""
        campaign = await CampaignService.get_by_id(db, campaign_id, tenant_id)
        if campaign is None:
            return None

        if campaign.status in ("completed", "cancelled"):
            return None

        campaign.status = "cancelled"
        await db.flush()
        await db.refresh(campaign)
        return campaign

    @staticmethod
    async def get_metrics(
        db: AsyncSession, campaign_id: str, tenant_id: str | None = None
    ) -> dict:
        """Get campaign metrics."""
        campaign = await CampaignService.get_by_id(db, campaign_id, tenant_id)
        if campaign is None:
            return {}

        return {
            "id": campaign.id,
            "name": campaign.name,
            "status": campaign.status,
            "total_contacts": campaign.total_contacts,
            "sent_count": campaign.sent_count,
            "failed_count": campaign.failed_count,
            "delivery_rate": round(
                (campaign.sent_count / campaign.total_contacts * 100) if campaign.total_contacts > 0 else 0,
                2,
            ),
            "started_at": campaign.started_at,
            "completed_at": campaign.completed_at,
        }
