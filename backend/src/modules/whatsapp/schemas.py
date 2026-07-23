"""WhatsApp schemas"""
from pydantic import BaseModel, Field
from typing import Optional

class WhatsAppConfig(BaseModel):
    api_url: str = "https://graph.facebook.com/v22.0"
    phone_number_id: str = ""
    api_key: str = ""
    verify_token: str = ""
    business_account_id: str = ""

class SendTextRequest(BaseModel):
    to: str
    text: str
    preview_url: bool = False

class SendMediaRequest(BaseModel):
    to: str
    media_url: str
    caption: Optional[str] = None
    media_type: str = "image"  # image/video/document/audio

class SendTemplateRequest(BaseModel):
    to: str
    template_name: str
    params: Optional[dict] = None
    language: str = "pt_BR"

class WebhookPayload(BaseModel):
    object: str
    entry: list

class MessageStatus(BaseModel):
    message_id: str
    status: str  # sent/delivered/read/failed
    timestamp: str

class WhatsAppMessageResponse(BaseModel):
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
