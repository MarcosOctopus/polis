"""Message service — send, list by conversation, mark as read, provider integration."""

from datetime import datetime, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Channel, Message
from src.modules.messages.schemas import MessageCreate
from src.providers.base import MessageProvider
from src.providers.email.provider import EmailProvider
from src.providers.sms.provider import SmsProvider
from src.providers.whatsapp.provider import WhatsAppProvider


def _get_provider(channel: Channel) -> MessageProvider:
    """Resolve the appropriate provider instance for a channel."""
    providers = {
        "whatsapp": WhatsAppProvider,
        "email": EmailProvider,
        "sms": SmsProvider,
    }
    provider_cls = providers.get(channel.provider)
    if provider_cls is None:
        raise ValueError(f"Unknown provider: {channel.provider}")
    return provider_cls(credentials=channel.credentials, config=channel.config)


class MessageService:
    """Business logic for message management."""

    @staticmethod
    async def create(
        db: AsyncSession,
        tenant_id: str,
        data: MessageCreate,
    ) -> Message:
        message = Message(
            tenant_id=tenant_id,
            conversation_id=data.conversation_id,
            channel_id=data.channel_id,
            direction=data.direction,
            message_type=data.message_type,
            content=data.content,
            provider_message_id=data.provider_message_id,
        )
        db.add(message)
        await db.flush()
        await db.refresh(message)
        return message

    @staticmethod
    async def send_and_create(
        db: AsyncSession,
        tenant_id: str,
        data: MessageCreate,
    ) -> Message:
        """Send a message through the channel's provider, then persist it."""
        message = Message(
            tenant_id=tenant_id,
            conversation_id=data.conversation_id,
            channel_id=data.channel_id,
            direction="outbound",
            message_type=data.message_type,
            content=data.content,
        )
        db.add(message)
        await db.flush()

        # If a channel is specified, send via provider
        if data.channel_id:
            result = await db.execute(
                select(Channel).where(
                    Channel.id == data.channel_id,
                    Channel.tenant_id == tenant_id,
                    Channel.is_active == True,  # noqa: E712
                )
            )
            channel = result.scalar_one_or_none()
            if channel:
                try:
                    provider = _get_provider(channel)
                    to_phone = data.content.get("to", "")
                    text_content = data.content.get("text", "")

                    if data.message_type == "text":
                        status = await provider.send_text(to_phone, text_content)
                    elif data.message_type == "media":
                        media_url = data.content.get("media_url", "")
                        caption = data.content.get("caption")
                        status = await provider.send_media(to_phone, media_url, caption)
                    elif data.message_type == "template":
                        template_name = data.content.get("template_name", "")
                        params = data.content.get("params")
                        status = await provider.send_template(to_phone, template_name, params)
                    else:
                        status = await provider.send_text(to_phone, text_content)

                    message.provider_message_id = status.provider_message_id
                    message.provider_status = status.status.value
                except Exception:
                    message.provider_status = "failed"
                    message.metadata = {"error": "Provider call failed"}

        await db.flush()
        await db.refresh(message)
        return message

    @staticmethod
    async def get_by_id(
        db: AsyncSession, message_id: str, tenant_id: str | None = None
    ) -> Message | None:
        query = select(Message).where(Message.id == message_id)
        if tenant_id:
            query = query.where(Message.tenant_id == tenant_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_by_conversation(
        db: AsyncSession,
        conversation_id: str,
        tenant_id: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Message], int]:
        query = select(Message).where(
            Message.conversation_id == conversation_id,
        )
        if tenant_id:
            query = query.where(Message.tenant_id == tenant_id)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(Message.created_at.asc()).offset(skip).limit(limit)
        result = await db.execute(query)
        messages = list(result.scalars().all())
        return messages, total

    @staticmethod
    async def mark_as_read(
        db: AsyncSession,
        message_id: str,
        tenant_id: str | None = None,
    ) -> Message | None:
        query = select(Message).where(Message.id == message_id)
        if tenant_id:
            query = query.where(Message.tenant_id == tenant_id)
        result = await db.execute(query)
        message = result.scalar_one_or_none()
        if message is None:
            return None

        message.is_read = True
        message.read_at = datetime.now(timezone.utc)
        await db.flush()
        await db.refresh(message)
        return message

    @staticmethod
    async def mark_conversation_messages_as_read(
        db: AsyncSession,
        conversation_id: str,
        tenant_id: str | None = None,
    ) -> int:
        """Mark all unread inbound messages in a conversation as read."""
        query = (
            update(Message)
            .where(
                Message.conversation_id == conversation_id,
                Message.direction == "inbound",
                Message.is_read == False,  # noqa: E712
            )
            .values(is_read=True, read_at=datetime.now(timezone.utc))
        )
        if tenant_id:
            query = query.where(Message.tenant_id == tenant_id)
        result = await db.execute(query)
        await db.flush()
        return result.rowcount
