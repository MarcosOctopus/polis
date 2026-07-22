"""Channel service — CRUD with credential encryption, connection testing, webhook registration."""

import json
import logging
import secrets
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import settings
from src.database.models import Channel
from src.modules.channels.schemas import ChannelCreate, ChannelUpdate

logger = logging.getLogger(__name__)

try:
    from cryptography.fernet import Fernet

    _fernet = None

    def _get_fernet() -> Fernet:
        global _fernet
        if _fernet is None:
            # Derive a Fernet key from the JWT secret (padded to 32 URL-safe base64 bytes)
            import base64
            import hashlib

            key = hashlib.sha256(settings.jwt_secret_key.encode()).digest()
            key_b64 = base64.urlsafe_b64encode(key)
            _fernet = Fernet(key_b64)
        return _fernet

    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False
    logger.warning("cryptography not installed — credentials stored in plaintext")

    def _get_fernet():
        return None


def _encrypt_credentials(credentials: dict) -> dict:
    """Encrypt credential values for storage."""
    if not HAS_CRYPTO:
        return credentials

    encrypted = {}
    fernet = _get_fernet()
    for key, value in credentials.items():
        if isinstance(value, str):
            encrypted[key] = fernet.encrypt(value.encode()).decode()
        else:
            encrypted[key] = fernet.encrypt(json.dumps(value).encode()).decode()
    return encrypted


def _decrypt_credentials(credentials: dict) -> dict:
    """Decrypt credential values for use."""
    if not HAS_CRYPTO:
        return credentials

    decrypted = {}
    fernet = _get_fernet()
    for key, value in credentials.items():
        try:
            decrypted[key] = fernet.decrypt(value.encode()).decode()
        except Exception:
            # Value might not be encrypted (e.g. during testing)
            decrypted[key] = value
    return decrypted


class ChannelService:
    """Business logic for channel management."""

    @staticmethod
    async def create(
        db: AsyncSession, tenant_id: str, data: ChannelCreate
    ) -> Channel:
        encrypted_creds = _encrypt_credentials(data.credentials)
        channel = Channel(
            tenant_id=tenant_id,
            name=data.name,
            provider=data.provider,
            channel_type=data.channel_type,
            credentials=encrypted_creds,
            config=data.config,
            is_active=True,
        )
        db.add(channel)
        await db.flush()
        await db.refresh(channel)
        return channel

    @staticmethod
    async def get_by_id(
        db: AsyncSession, channel_id: str, tenant_id: str | None = None
    ) -> Channel | None:
        query = select(Channel).where(
            Channel.id == channel_id,
            Channel.deleted_at.is_(None),
        )
        if tenant_id:
            query = query.where(Channel.tenant_id == tenant_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_decrypted(
        db: AsyncSession, channel_id: str, tenant_id: str | None = None
    ) -> tuple[Channel, dict] | None:
        """Get a channel with its credentials decrypted."""
        channel = await ChannelService.get_by_id(db, channel_id, tenant_id)
        if channel is None:
            return None
        decrypted = _decrypt_credentials(channel.credentials)
        return channel, decrypted

    @staticmethod
    async def list_by_tenant(
        db: AsyncSession,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        provider: str | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[Channel], int]:
        query = select(Channel).where(
            Channel.tenant_id == tenant_id,
            Channel.deleted_at.is_(None),
        )
        if provider:
            query = query.where(Channel.provider == provider)
        if is_active is not None:
            query = query.where(Channel.is_active == is_active)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(Channel.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        channels = list(result.scalars().all())
        return channels, total

    @staticmethod
    async def update(
        db: AsyncSession,
        channel_id: str,
        data: ChannelUpdate,
        tenant_id: str | None = None,
    ) -> Channel | None:
        channel = await ChannelService.get_by_id(db, channel_id, tenant_id)
        if channel is None:
            return None

        update_data = data.model_dump(exclude_unset=True, exclude={"credentials"})
        for key, value in update_data.items():
            setattr(channel, key, value)

        if data.credentials is not None:
            channel.credentials = _encrypt_credentials(data.credentials)

        await db.flush()
        await db.refresh(channel)
        return channel

    @staticmethod
    async def soft_delete(
        db: AsyncSession, channel_id: str, tenant_id: str | None = None
    ) -> bool:
        channel = await ChannelService.get_by_id(db, channel_id, tenant_id)
        if channel is None:
            return False

        channel.deleted_at = datetime.now(timezone.utc)
        channel.is_active = False
        await db.flush()
        return True

    @staticmethod
    async def test_connection(
        db: AsyncSession, channel_id: str, tenant_id: str | None = None
    ) -> tuple[bool, str]:
        """Test the connection to a channel's provider."""
        result = await ChannelService.get_decrypted(db, channel_id, tenant_id)
        if result is None:
            return False, "Channel not found"

        channel, decrypted_creds = result

        try:
            from src.providers.email.provider import EmailProvider
            from src.providers.sms.provider import SmsProvider
            from src.providers.whatsapp.provider import WhatsAppProvider

            providers = {
                "whatsapp": WhatsAppProvider,
                "email": EmailProvider,
                "sms": SmsProvider,
            }
            provider_cls = providers.get(channel.provider)
            if provider_cls is None:
                return False, f"Unknown provider: {channel.provider}"

            provider = provider_cls(credentials=decrypted_creds, config=channel.config)

            # Send a test message to a configurable test number
            test_to = (channel.config or {}).get("test_number", "")
            if not test_to:
                return True, "Connection configured (no test number to validate)"

            status = await provider.send_text(test_to, "Teste de conexão - Polis")
            if status.status.value in ("sent", "queued"):
                return True, f"Connection successful (status: {status.status.value})"
            return False, f"Connection failed (status: {status.status.value}, error: {status.error})"

        except Exception as exc:
            logger.exception("Connection test failed for channel %s", channel_id)
            return False, f"Connection error: {str(exc)}"

    @staticmethod
    async def register_webhook(
        db: AsyncSession,
        channel_id: str,
        webhook_url: str,
        tenant_id: str | None = None,
    ) -> tuple[Channel, str]:
        """Register a webhook URL for a channel and generate a webhook secret."""
        channel = await ChannelService.get_by_id(db, channel_id, tenant_id)
        if channel is None:
            raise ValueError("Channel not found")

        webhook_secret = secrets.token_hex(32)
        channel.webhook_url = webhook_url
        channel.webhook_secret = webhook_secret
        await db.flush()
        await db.refresh(channel)
        return channel, webhook_secret
