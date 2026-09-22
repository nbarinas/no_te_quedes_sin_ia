import json
from typing import Optional

from fastapi import APIRouter, Request, HTTPException, Query

from app.config import get_settings
from app.sheets import get_sheets_client
from app.whatsapp import get_whatsapp_client

router = APIRouter()


@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
):
    settings = get_settings()
    if hub_mode == "subscribe" and hub_verify_token == settings.meta_verify_token:
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Verificación fallida")


@router.post("/webhook")
async def receive_webhook(request: Request):
    body = await request.body()
    sheets = get_sheets_client()

    signature = request.headers.get("X-Hub-Signature-256", "")
    wa = get_whatsapp_client()
    if not wa.verify_signature(body, signature):
        raise HTTPException(status_code=403, detail="Firma inválida")

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="JSON inválido")

    entries = data.get("entry", [])
    for entry in entries:
        for change in entry.get("changes", []):
            value = change.get("value", {})
            messages = value.get("messages", [])
            statuses = value.get("statuses", [])

            for message in messages:
                phone = message.get("from")
                msg_type = message.get("type")
                text = ""
                if msg_type == "text":
                    text = message.get("text", {}).get("body", "")
                elif msg_type == "button":
                    text = message.get("button", {}).get("text", "")
                elif msg_type == "interactive":
                    text = message.get("interactive", {}).get("button_reply", {}).get("title", "")

                if phone and text:
                    sheets.add_conversation(phone, "entrante", text, agente="usuario")

            for status in statuses:
                phone = status.get("recipient_id")
                status_value = status.get("status")
                if phone and status_value:
                    if status_value in ("failed", "undeliverable"):
                        sheets.update_contact_status(phone, "error", notas=f"Estado: {status_value}")

    return {"status": "ok"}
