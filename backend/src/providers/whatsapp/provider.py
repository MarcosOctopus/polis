"""WhatsApp provider — generic implementation using a REST API pattern."""

import logging
from datetime import datetime, timezone

import httpx

from src.providers.base import (
    DeliveryStatus,
    IncomingMessage,
    MessageProvider,
    MessageStatus,
)

logger = logging.getLogger(__name__)


class WhatsAppProvider(MessageProvider):
    """Generic WhatsApp provider.
    
    Expects credentials dict with:
        - api_url: Base URL for the WhatsApp Business API
        - api_key: API key or token for authentication
        - phone_number_id: The sender's phone number ID
    """

    BASE_HEADERS = {"Content-Type": "application/json"}

    async def _post(self, endpoint: str, payload: dict) -> dict:
        """Make an HTTP POST request to the provider API."""
        url = f"{self.credentials['api_url'].rstrip('/')}/{endpoint}"
        headers = {**self.BASE_HEADERS, "Authorization": f"Bearer {self.credentials['api_key']}"}
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()

    async def _get(self, endpoint: str) -> dict:
        """Make an HTTP GET request to the provider API."""
        url = f"{self.credentials['api_url'].rstrip('/')}/{endpoint}"
        headers = {**self.BASE_HEADERS, "Authorization": f"Bearer {self.credentials['api_key']}"}
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.json()

    async def send_text(self, to: str, text: str) -> MessageStatus:
        """Send a WhatsApp text message."""
        phone_id = self.credentials["phone_number_id"]
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text},
        }
        try:
            response = await self._post(f"{phone_id}/messages", payload)
            msg_id = response.get("messages", [{}])[0].get("id", "")
            return MessageStatus(
                provider_message_id=msg_id,
                status=DeliveryStatus.SENT,
                raw_response=response,
            )
        except Exception as exc:
            logger.exception("Failed to send WhatsApp text to %s", to)
            return MessageStatus(
                provider_message_id="",
                status=DeliveryStatus.FAILED,
                error=str(exc),
            )

    async def send_media(self, to: str, media_url: str, caption: str | None = None) -> MessageStatus:
        """Send a WhatsApp media message."""
        phone_id = self.credentials["phone_number_id"]
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "image",
            "image": {"link": media_url},
        }
        if caption:
            payload["image"]["caption"] = caption
        try:
            response = await self._post(f"{phone_id}/messages", payload)
            msg_id = response.get("messages", [{}])[0].get("id", "")
            return MessageStatus(
                provider_message_id=msg_id,
                status=DeliveryStatus.SENT,
                raw_response=response,
            )
        except Exception as exc:
            logger.exception("Failed to send WhatsApp media to %s", to)
            return MessageStatus(
                provider_message_id="",
                status=DeliveryStatus.FAILED,
                error=str(exc),
            )

    async def send_template(self, to: str, template_name: str, params: dict | None = None) -> MessageStatus:
        """Send a WhatsApp template message."""
        phone_id = self.credentials["phone_number_id"]
        components: list = []
        if params:
            components.append(
                {
                    "type": "body",
                    "parameters": [{"type": "text", "text": v} for v in params.values()],
                }
            )
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": self.config.get("language", "pt_BR")},
            },
        }
        if components:
            payload["template"]["components"] = components

        try:
            response = await self._post(f"{phone_id}/messages", payload)
            msg_id = response.get("messages", [{}])[0].get("id", "")
            return MessageStatus(
                provider_message_id=msg_id,
                status=DeliveryStatus.SENT,
                raw_response=response,
            )
        except Exception as exc:
            logger.exception("Failed to send WhatsApp template to %s", to)
            return MessageStatus(
                provider_message_id="",
                status=DeliveryStatus.FAILED,
                error=str(exc),
            )

    async def get_status(self, message_id: str) -> DeliveryStatus:
        """Check WhatsApp message delivery status."""
        phone_id = self.credentials["phone_number_id"]
        try:
            response = await self._get(f"{phone_id}/messages/{message_id}")
            status = response.get("messages", [{}])[0].get("status", "sent")
            mapping = {
                "accepted": DeliveryStatus.QUEUED,
                "sent": DeliveryStatus.SENT,
                "delivered": DeliveryStatus.DELIVERED,
                "read": DeliveryStatus.READ,
                "failed": DeliveryStatus.FAILED,
            }
            return mapping.get(status, DeliveryStatus.SENT)
        except Exception as exc:
            logger.exception("Failed to get status for message %s", message_id)
            return DeliveryStatus.FAILED

    async def process_webhook(self, data: dict) -> IncomingMessage | None:
        """Parse a WhatsApp Business API webhook payload."""
        try:
            entries = data.get("entry", [])
            if not entries:
                return None
            changes = entries[0].get("changes", [])
            if not changes:
                return None
            value = changes[0].get("value", {})
            messages = value.get("messages", [])
            if not messages:
                return None
            msg = messages[0]
            msg_id = msg.get("id", "")
            from_number = msg.get("from", "")
            to_number = value.get("metadata", {}).get("display_phone_number", "")

            text = None
            media_urls = None
            if msg.get("type") == "text":
                text = msg.get("text", {}).get("body", "")
            elif msg.get("type") in ("image", "video", "audio", "document"):
                media_type = msg.get("type")
                media_obj = msg.get(media_type, {})
                media_urls = [media_obj.get("link", "")] if media_obj.get("link") else None
                text = media_obj.get("caption", "")

            return IncomingMessage(
                provider_message_id=msg_id,
                from_number=from_number,
                to_number=to_number,
                text=text,
                media_urls=media_urls,
                timestamp=datetime.now(timezone.utc),
                raw_data=data,
            )
        except Exception as exc:
            logger.exception("Failed to process WhatsApp webhook")
            return None
