"""WhatsApp Service — Meta Cloud API integration"""
import json
import logging
from datetime import datetime, timezone
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

API_BASE = "https://graph.facebook.com/v22.0"


class WhatsAppCloudService:
    """Service for WhatsApp Cloud API (Meta). Isolated per project."""

    def __init__(self, phone_number_id: str, api_key: str):
        self.phone_number_id = phone_number_id
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def send_text(self, to: str, text: str, preview_url: bool = False) -> dict:
        """Send a text message via WhatsApp Cloud API."""
        url = f"{API_BASE}/{self.phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text, "preview_url": preview_url},
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload, headers=self.headers)
            result = resp.json()
            if resp.status_code != 200:
                logger.error("WhatsApp send_text failed: %s", result)
            return {"status": resp.status_code, "response": result}

    async def send_media(
        self, to: str, media_url: str, caption: Optional[str] = None, media_type: str = "image"
    ) -> dict:
        """Send a media message (image/video/document/audio)."""
        url = f"{API_BASE}/{self.phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": media_type,
            media_type: {"link": media_url},
        }
        if caption:
            payload[media_type]["caption"] = caption
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload, headers=self.headers)
            result = resp.json()
            if resp.status_code != 200:
                logger.error("WhatsApp send_media failed: %s", result)
            return {"status": resp.status_code, "response": result}

    async def send_template(
        self, to: str, template_name: str, params: Optional[dict] = None, language: str = "pt_BR"
    ) -> dict:
        """Send a template message (for notifications/proactive)."""
        url = f"{API_BASE}/{self.phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language},
            },
        }
        if params:
            components = [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": str(v)} for v in params.values()
                    ],
                }
            ]
            payload["template"]["components"] = components

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload, headers=self.headers)
            result = resp.json()
            if resp.status_code != 200:
                logger.error("WhatsApp send_template failed: %s", result)
            return {"status": resp.status_code, "response": result}

    async def get_message_status(self, message_id: str) -> dict:
        """Check delivery status of a message."""
        url = f"{API_BASE}/{self.phone_number_id}/messages/{message_id}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers=self.headers)
            return {"status": resp.status_code, "response": resp.json()}

    async def register_webhook(self, webhook_url: str, verify_token: str) -> dict:
        """Register webhook subscription for the WhatsApp Business Account."""
        url = f"{API_BASE}/{self.phone_number_id}/subscribed_apps"
        payload = {"webhook_url": webhook_url, "verify_token": verify_token}
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload, headers=self.headers)
            return {"status": resp.status_code, "response": resp.json()}

    @staticmethod
    def verify_webhook(mode: str, token: str, verify_token: str) -> bool:
        """Verify WhatsApp webhook challenge (GET request)."""
        return mode == "subscribe" and token == verify_token

    @staticmethod
    def parse_incoming_message(data: dict) -> Optional[dict]:
        """Parse incoming WhatsApp webhook payload into a structured message."""
        try:
            entry = data.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [])
            if not messages:
                return None

            msg = messages[0]
            msg_id = msg.get("id", "")
            from_number = msg.get("from", "")
            msg_type = msg.get("type", "text")
            timestamp = msg.get("timestamp", "")

            parsed = {
                "message_id": msg_id,
                "from": from_number,
                "type": msg_type,
                "timestamp": timestamp,
                "text": None,
                "media_url": None,
                "media_id": None,
                "location": None,
            }

            if msg_type == "text":
                parsed["text"] = msg.get("text", {}).get("body", "")
            elif msg_type in ("image", "video", "audio", "document"):
                media = msg.get(msg_type, {})
                parsed["media_id"] = media.get("id", "")
                parsed["text"] = media.get("caption", "")
            elif msg_type == "location":
                parsed["location"] = msg.get("location", {})

            # Contact info
            contacts = value.get("contacts", [{}])
            if contacts:
                profile = contacts[0].get("profile", {})
                parsed["sender_name"] = profile.get("name", "")
                parsed["wa_id"] = contacts[0].get("wa_id", "")

            parsed["raw"] = data
            return parsed
        except Exception as exc:
            logger.exception("Failed to parse WhatsApp webhook: %s", exc)
            return None

    async def health_check(self) -> dict:
        """Check if the WhatsApp API is accessible."""
        url = f"{API_BASE}/{self.phone_number_id}"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(url, headers=self.headers)
                return {"online": resp.status_code == 200, "code": resp.status_code}
        except Exception as exc:
            return {"online": False, "error": str(exc)}
