"""Email provider — SMTP or Resend API implementation."""

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


class EmailProvider(MessageProvider):
    """Email message provider.
    
    Supports two modes:
        1. Resend API (when credentials contain 'api_key')
        2. SMTP (when credentials contain 'smtp_host', 'smtp_port', 'smtp_user', 'smtp_pass')
    
    Credentials:
        - mode: "resend" | "smtp"
        - api_key: Resend API key (for resend mode)
        - smtp_host: SMTP server host (for smtp mode)
        - smtp_port: SMTP server port (for smtp mode)
        - smtp_user: SMTP username (for smtp mode)
        - smtp_pass: SMTP password (for smtp mode)
        - from_email: Sender email address
        - from_name: Optional sender display name
    
    Config:
        - reply_to: Optional reply-to address
    """

    def __init__(self, credentials: dict, config: dict | None = None):
        super().__init__(credentials, config)
        self.mode = credentials.get("mode", "resend")
        self.from_email = credentials.get("from_email", "")
        self.from_name = credentials.get("from_name", "")

    async def _send_resend(self, to: str, subject: str, html_body: str) -> MessageStatus:
        """Send email via Resend API."""
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {self.credentials['api_key']}",
            "Content-Type": "application/json",
        }
        payload = {
            "from": f"{self.from_name} <{self.from_email}>" if self.from_name else self.from_email,
            "to": [to],
            "subject": subject,
            "html": html_body,
        }
        if self.config and self.config.get("reply_to"):
            payload["reply_to"] = self.config["reply_to"]

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
            return MessageStatus(
                provider_message_id=data.get("id", ""),
                status=DeliveryStatus.SENT,
                raw_response=data,
            )
        except Exception as exc:
            logger.exception("Failed to send email via Resend to %s", to)
            return MessageStatus(
                provider_message_id="",
                status=DeliveryStatus.FAILED,
                error=str(exc),
            )

    async def _send_smtp(self, to: str, subject: str, html_body: str) -> MessageStatus:
        """Send email via SMTP.
        
        Uses aio smtplib for async SMTP delivery.
        """
        try:
            import aiosmtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText

            msg = MIMEMultipart("alternative")
            msg["From"] = f"{self.from_name} <{self.from_email}>" if self.from_name else self.from_email
            msg["To"] = to
            msg["Subject"] = subject
            msg.attach(MIMEText(html_body, "html"))

            host = self.credentials.get("smtp_host", "localhost")
            port = int(self.credentials.get("smtp_port", "587"))
            username = self.credentials.get("smtp_user", "")
            password = self.credentials.get("smtp_pass", "")

            await aiosmtplib.send(
                msg,
                hostname=host,
                port=port,
                username=username or None,
                password=password or None,
                use_tls=port == 465,
                start_tls=port != 465,
            )

            return MessageStatus(
                provider_message_id=msg["Message-ID"] or "",
                status=DeliveryStatus.SENT,
            )
        except ImportError:
            logger.error("aiosmtplib is not installed. Install it with: pip install aiosmtplib")
            return MessageStatus(
                provider_message_id="",
                status=DeliveryStatus.FAILED,
                error="aiosmtplib not installed",
            )
        except Exception as exc:
            logger.exception("Failed to send email via SMTP to %s", to)
            return MessageStatus(
                provider_message_id="",
                status=DeliveryStatus.FAILED,
                error=str(exc),
            )

    async def send_text(self, to: str, text: str) -> MessageStatus:
        """Send a plain text email."""
        html_body = text.replace("\n", "<br>")
        subject = self.config.get("default_subject", "Mensagem")
        return await self._send_resend(to, subject, html_body) if self.mode == "resend" \
            else await self._send_smtp(to, subject, html_body)

    async def send_media(self, to: str, media_url: str, caption: str | None = None) -> MessageStatus:
        """Send an email with a media link."""
        body = f"{caption or ''}<br><br><img src=\"{media_url}\" style=\"max-width:100%\"/>" if media_url else caption or ""
        subject = self.config.get("default_subject", "Mídia")
        return await self._send_resend(to, subject, body) if self.mode == "resend" \
            else await self._send_smtp(to, subject, body)

    async def send_template(self, to: str, template_name: str, params: dict | None = None) -> MessageStatus:
        """Send a template-based email."""
        body = f"<h1>{template_name}</h1><p>Template parameters: {params or {}}</p>"
        subject = template_name.replace("_", " ").title()
        return await self._send_resend(to, subject, body) if self.mode == "resend" \
            else await self._send_smtp(to, subject, body)

    async def get_status(self, message_id: str) -> DeliveryStatus:
        """Check email delivery status (Resend API only)."""
        if self.mode != "resend":
            logger.warning("Status check not supported for SMTP mode")
            return DeliveryStatus.SENT
        try:
            url = f"https://api.resend.com/emails/{message_id}"
            headers = {"Authorization": f"Bearer {self.credentials['api_key']}"}
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                data = resp.json()
            status = data.get("last_event", "sent")
            mapping = {
                "delivered": DeliveryStatus.DELIVERED,
                "bounced": DeliveryStatus.FAILED,
                "complained": DeliveryStatus.REJECTED,
                "sent": DeliveryStatus.SENT,
            }
            return mapping.get(status, DeliveryStatus.SENT)
        except Exception as exc:
            logger.exception("Failed to get email status for %s", message_id)
            return DeliveryStatus.FAILED

    async def process_webhook(self, data: dict) -> IncomingMessage | None:
        """Process an incoming email webhook (Resend inbound)."""
        try:
            email = data.get("email", data)
            subject = email.get("subject", "")
            from_addr = email.get("from", "")
            to_addr = email.get("to", "")
            text = email.get("text", email.get("html", ""))
            message_id = email.get("id", email.get("message_id", ""))

            return IncomingMessage(
                provider_message_id=message_id,
                from_number=from_addr,
                to_number=to_addr,
                text=text,
                timestamp=datetime.now(timezone.utc),
                raw_data=data,
            )
        except Exception as exc:
            logger.exception("Failed to process email webhook")
            return None
