"""WhatsApp Router — webhook + send endpoints, isolated within Polis"""
import logging

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel
from typing import Optional

from src.modules.whatsapp.schemas import (
    SendTextRequest,
    SendMediaRequest,
    SendTemplateRequest,
    WhatsAppMessageResponse,
)
from src.modules.whatsapp.service import WhatsAppCloudService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

# Will be configured at startup from settings
_service: Optional[WhatsAppCloudService] = None
_verify_token: str = ""
_configured: bool = False


def configure(phone_number_id: str, api_key: str, verify_token: str):
    """Initialize WhatsApp service with credentials."""
    global _service, _verify_token, _configured
    if phone_number_id and api_key:
        _service = WhatsAppCloudService(phone_number_id, api_key)
        _verify_token = verify_token
        _configured = True
        logger.info("WhatsApp service configured for Polis")
    else:
        _configured = False
        logger.warning("WhatsApp service NOT configured — missing credentials")


# ─── Webhook ───

@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query("", alias="hub.mode"),
    hub_verify_token: str = Query("", alias="hub.verify_token"),
    hub_challenge: str = Query("", alias="hub.challenge"),
):
    """Handle WhatsApp webhook verification (GET from Meta)."""
    if WhatsAppCloudService.verify_webhook(hub_mode, hub_verify_token, _verify_token):
        return int(hub_challenge) if hub_challenge.isdigit() else hub_challenge
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhook")
async def receive_webhook(request: Request):
    """Receive incoming WhatsApp messages via webhook."""
    body = await request.json()
    parsed = WhatsAppCloudService.parse_incoming_message(body)
    if not parsed:
        return {"status": "ignored"}

    logger.info("WhatsApp message received from %s: %s", parsed["from"], parsed.get("text", "[media]"))

    # TODO: Save to Polis database, create conversation, trigger notifications
    # TODO: If it's a complaint-related message, route to the appropriate handler

    return {"status": "received", "message_id": parsed["message_id"]}


# ─── Send Messages ───

@router.post("/send/text", response_model=WhatsAppMessageResponse)
async def send_text(request: SendTextRequest):
    """Send a WhatsApp text message."""
    if not _configured or not _service:
        raise HTTPException(status_code=503, detail="WhatsApp not configured")
    result = await _service.send_text(request.to, request.text, request.preview_url)
    resp = result["response"]
    msg_id = resp.get("messages", [{}])[0].get("id", "") if result["status"] == 200 else None
    return WhatsAppMessageResponse(
        success=result["status"] == 200,
        message_id=msg_id,
        error=None if result["status"] == 200 else resp.get("error", {}).get("message", "Unknown"),
    )


@router.post("/send/media", response_model=WhatsAppMessageResponse)
async def send_media(request: SendMediaRequest):
    """Send a media message via WhatsApp."""
    if not _configured or not _service:
        raise HTTPException(status_code=503, detail="WhatsApp not configured")
    result = await _service.send_media(request.to, request.media_url, request.caption, request.media_type)
    resp = result["response"]
    msg_id = resp.get("messages", [{}])[0].get("id", "") if result["status"] == 200 else None
    return WhatsAppMessageResponse(
        success=result["status"] == 200,
        message_id=msg_id,
        error=None if result["status"] == 200 else resp.get("error", {}).get("message", "Unknown"),
    )


@router.post("/send/template", response_model=WhatsAppMessageResponse)
async def send_template(request: SendTemplateRequest):
    """Send a template message."""
    if not _configured or not _service:
        raise HTTPException(status_code=503, detail="WhatsApp not configured")
    result = await _service.send_template(request.to, request.template_name, request.params, request.language)
    resp = result["response"]
    msg_id = resp.get("messages", [{}])[0].get("id", "") if result["status"] == 200 else None
    return WhatsAppMessageResponse(
        success=result["status"] == 200,
        message_id=msg_id,
        error=None if result["status"] == 200 else resp.get("error", {}).get("message", "Unknown"),
    )


# ─── Status ───

@router.get("/status")
async def whatsapp_status():
    """Health check for the WhatsApp service."""
    if not _configured or not _service:
        return {"configured": False, "online": False}
    health = await _service.health_check()
    return {"configured": True, **health}


@router.get("/messages/{message_id}/status")
async def message_status(message_id: str):
    """Check delivery status of a sent message."""
    if not _configured or not _service:
        raise HTTPException(status_code=503, detail="WhatsApp not configured")
    result = await _service.get_message_status(message_id)
    return result["response"]
