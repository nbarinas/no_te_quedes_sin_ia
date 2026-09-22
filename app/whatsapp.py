import hmac
import hashlib
from typing import Optional

import httpx

from app.config import get_settings

META_API_VERSION = "v18.0"


class WhatsAppClient:
    def __init__(self):
        self.settings = get_settings()
        self.base_url = f"https://graph.facebook.com/{META_API_VERSION}"
        self.headers = {
            "Authorization": f"Bearer {self.settings.meta_access_token}",
            "Content-Type": "application/json",
        }

    async def send_template(self, to: str, template_name: str, language: str = "es", variables: Optional[list] = None):
        url = f"{self.base_url}/{self.settings.meta_phone_number_id}/messages"

        components = []
        if variables:
            body_params = [{"type": "text", "text": str(v)} for v in variables]
            components.append({
                "type": "body",
                "parameters": body_params,
            })

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self._normalize_phone(to),
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language},
            },
        }

        if components:
            payload["template"]["components"] = components

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()

    async def send_text_message(self, to: str, text: str):
        url = f"{self.base_url}/{self.settings.meta_phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self._normalize_phone(to),
            "type": "text",
            "text": {"body": text},
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()

    def _normalize_phone(self, phone: str) -> str:
        cleaned = "".join(c for c in phone if c.isdigit())
        return cleaned

    def verify_signature(self, body: bytes, signature: str) -> bool:
        if not self.settings.meta_app_secret:
            return True
        expected = hmac.new(
            self.settings.meta_app_secret.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(f"sha256={expected}", signature)


def get_whatsapp_client() -> WhatsAppClient:
    return WhatsAppClient()
