"""SMS provider — Zenvia or Twilio implementation."""

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


class SmsProvider(MessageProvider):
    """SMS message provider.
    
    Supports two backends:
        1. Twilio (when credentials contain 'account_sid' and 'auth_token')
        2. Zenvia (when credentials contain 'api_key' for Zenvia API)
    
    Credentials:
        - mode: "twilio" | "zenvia"
        
        Twilio:
        - account_sid: Twilio Account SID
        - auth_token: Twilio Auth Token
        - from_number: Sender phone number
        
        Zenvia:
        - api_key: Zenvia API key
        - from_number: Sender identifier (short code or number)
    
    Config:
        - callback_url: Optional status callback URL
    """

    def __init__(self, credentials: dict, config: dict | None = None):
        super().__init__(credentials, config)
        self.mode = credentials.get("mode", "twilio")
        self.from_number = credentials.get("from_number", "")

    async def _send_twilio(self, to: str, body: str) -> MessageStatus:
        """Send SMS via Twilio API."""
        account_sid = self.credentials["account_sid"]
        auth_token = self.credentials["auth_token"]
        url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"

        payload = {
            "To": to,
            "From": self.from_number,
            "Body": body,
        }
        if self.config and self.config.get("callback_url"):
            payload["StatusCallback"] = self.config["callback_url"]

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, data=payload, auth=(account_sid, auth_token))
                resp.raise_for_status()
                data = resp.json()
            return MessageStatus(
                provider_message_id=data.get("sid", ""),
                status=DeliveryStatus.SENT,
                raw_response=data,
            )
        except Exception as exc:
            logger.exception("Failed to send SMS via Twilio to %s", to)
            return MessageStatus(
                provider_message_id="",
                status=DeliveryStatus.FAILED,
                error=str(exc),
            )

    async def _send_zenvia(self, to: str, body: str) -> MessageStatus:
        """Send SMS via Zenvia API."""
        api_key = self.credentials["api_key"]
        url = "https://api.zenvia.com/v2/channels/sms/messages"

        headers = {
            "X-API-TOKEN": api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "from": self.from_number,
            "to": to,
            "contents": [{"type": "text", "text": body}],
        }
        if self.config and self.config.get("callback_url"):
            payload["callbackUrl"] = self.config["callback_url"]

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
            msg_id = data.get("id", "")
            return MessageStatus(
                provider_message_id=msg_id,
                status=DeliveryStatus.SENT,
                raw_response=data,
            )
        except Exception as exc:
            logger.exception("Failed to send SMS via Zenvia to %s", to)
            return MessageStatus(
                provider_message_id="",
                status=DeliveryStatus.FAILED,
                error=str(exc),
            )

    async def send_text(self, to: str, text: str) -> MessageStatus:
        """Send an SMS text message."""
        if self.mode == "twilio":
            return await self._send_twilio(to, text)
        return await self._send_zenvia(to, text)

    async def send_media(self, to: str, media_url: str, caption: str | None = None) -> MessageStatus:
        """Send an MMS message (Twilio only, media URL included)."""
        if self.mode != "twilio":
            logger.warning("Media messages not supported on non-Twilio SMS providers")
            return await self.send_text(to, caption or "Mídia")
        account_sid = self.credentials["account_sid"]
        auth_token = self.credentials["auth_token"]
        url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"

        payload = {
            "To": to,
            "From": self.from_number,
            "Body": caption or "",
            "MediaUrl": media_url,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, data=payload, auth=(account_sid, auth_token))
                resp.raise_for_status()
                data = resp.json()
            return MessageStatus(
                provider_message_id=data.get("sid", ""),
                status=DeliveryStatus.SENT,
                raw_response=data,
            )
        except Exception as exc:
            logger.exception("Failed to send MMS via Twilio to %s", to)
            return MessageStatus(
                provider_message_id="",
                status=DeliveryStatus.FAILED,
                error=str(exc),
            )

    async def send_template(self, to: str, template_name: str, params: dict | None = None) -> MessageStatus:
        """Send a templated SMS."""
        text = template_name
        if params:
            text = template_name.format(**params)
        return await self.send_text(to, text)

    async def get_status(self, message_id: str) -> DeliveryStatus:
        """Check SMS delivery status."""
        if self.mode == "twilio":
            account_sid = self.credentials["account_sid"]
            auth_token = self.credentials["auth_token"]
            url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages/{message_id}.json"

            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.get(url, auth=(account_sid, auth_token))
                    resp.raise_for_status()
                    data = resp.json()
                status = data.get("status", "sent")
                mapping = {
                    "queued": DeliveryStatus.QUEUED,
                    "sent": DeliveryStatus.SENT,
                    "delivered": DeliveryStatus.DELIVERED,
                    "read": DeliveryStatus.READ,
                    "failed": DeliveryStatus.FAILED,
                    "undelivered": DeliveryStatus.FAILED,
                }
                return mapping.get(status, DeliveryStatus.SENT)
            except Exception as exc:
                logger.exception("Failed to get Twilio status for %s", message_id)
                return DeliveryStatus.FAILED
        else:
            # Zenvia — basic status check
            try:
                api_key = self.credentials["api_key"]
                url = f"https://api.zenvia.com/v2/messages/{message_id}"
                headers = {"X-API-TOKEN": api_key}
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.get(url, headers=headers)
                    resp.raise_for_status()
                    data = resp.json()
                status = data.get("status", "sent")
                mapping = {
                    "SCHEDULED": DeliveryStatus.QUEUED,
                    "SENT": DeliveryStatus.SENT,
                    "DELIVERED": DeliveryStatus.DELIVERED,
                    "READ": DeliveryStatus.READ,
                    "FAILED": DeliveryStatus.FAILED,
                    "REJECTED": DeliveryStatus.REJECTED,
                }
                return mapping.get(status, DeliveryStatus.SENT)
            except Exception as exc:
                logger.exception("Failed to get Zenvia status for %s", message_id)
                return DeliveryStatus.FAILED

    async def process_webhook(self, data: dict) -> IncomingMessage | None:
        """Process an incoming SMS webhook.
        
        Handles both Twilio and Zenvia webhook formats.
        """
        try:
            # Twilio format
            if data.get("MessageSid"):
                return IncomingMessage(
                    provider_message_id=data["MessageSid"],
                    from_number=data.get("From", ""),
                    to_number=data.get("To", ""),
                    text=data.get("Body", ""),
                    timestamp=datetime.now(timezone.utc),
                    raw_data=data,
                )
            # Zenvia format
            if data.get("id") and data.get("channel") == "sms":
                msg = data
                return IncomingMessage(
                    provider_message_id=msg.get("id", ""),
                    from_number=msg.get("from", msg.get("mobile", "")),
                    to_number=msg.get("to", ""),
                    text=msg.get("text", ""),
                    timestamp=datetime.now(timezone.utc),
                    raw_data=data,
                )
            return None
        except Exception as exc:
            logger.exception("Failed to process SMS webhook")
            return None
