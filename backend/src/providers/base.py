"""Abstract base class for message providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class DeliveryStatus(str, Enum):
    """Delivery status for a sent message."""
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    REJECTED = "rejected"


@dataclass
class MessageStatus:
    """Result of sending a message through a provider."""
    provider_message_id: str
    status: DeliveryStatus
    raw_response: dict | None = None
    error: str | None = None


@dataclass
class IncomingMessage:
    """Parsed incoming message from a provider webhook."""
    provider_message_id: str
    from_number: str
    to_number: str
    text: str | None = None
    media_urls: list[str] | None = None
    timestamp: datetime | None = None
    raw_data: dict | None = None


class MessageProvider(ABC):
    """Abstract base class that all message providers must implement."""

    def __init__(self, credentials: dict, config: dict | None = None):
        self.credentials = credentials
        self.config = config or {}

    @abstractmethod
    async def send_text(self, to: str, text: str) -> MessageStatus:
        """Send a plain text message to a recipient.
        
        Args:
            to: The recipient identifier (phone number, email address, etc.).
            text: The plain text content.
        
        Returns:
            MessageStatus with provider's message ID and delivery status.
        """
        ...

    @abstractmethod
    async def send_media(self, to: str, media_url: str, caption: str | None = None) -> MessageStatus:
        """Send a media message (image, video, audio, document).
        
        Args:
            to: The recipient identifier.
            media_url: Public URL of the media file.
            caption: Optional caption text.
        
        Returns:
            MessageStatus with provider's message ID and delivery status.
        """
        ...

    @abstractmethod
    async def send_template(self, to: str, template_name: str, params: dict | None = None) -> MessageStatus:
        """Send a template message (pre-approved message template).
        
        Args:
            to: The recipient identifier.
            template_name: Name or ID of the template.
            params: Key-value pairs for template variable substitution.
        
        Returns:
            MessageStatus with provider's message ID and delivery status.
        """
        ...

    @abstractmethod
    async def get_status(self, message_id: str) -> DeliveryStatus:
        """Check the delivery status of a previously sent message.
        
        Args:
            message_id: The provider's message ID.
        
        Returns:
            Current DeliveryStatus.
        """
        ...

    @abstractmethod
    async def process_webhook(self, data: dict) -> IncomingMessage | None:
        """Parse an incoming webhook payload from the provider.
        
        Args:
            data: Raw webhook payload from the provider.
        
        Returns:
            Parsed IncomingMessage or None if the payload is not a message event.
        """
        ...
