import os
import json
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self):
        self.meta_access_token: str = os.getenv("META_ACCESS_TOKEN", "")
        self.meta_phone_number_id: str = os.getenv("META_PHONE_NUMBER_ID", "")
        self.meta_verify_token: str = os.getenv("META_VERIFY_TOKEN", "")
        self.meta_app_secret: Optional[str] = os.getenv("META_APP_SECRET")

        self.google_sheets_credentials_json: str = os.getenv(
            "GOOGLE_SHEETS_CREDENTIALS_JSON", ""
        )
        self.google_sheets_spreadsheet_id: str = os.getenv(
            "GOOGLE_SHEETS_SPREADSHEET_ID", ""
        )

        self.app_secret_key: str = os.getenv("APP_SECRET_KEY", "change-me")
        self.app_host: str = os.getenv("APP_HOST", "0.0.0.0")
        self.app_port: int = int(os.getenv("APP_PORT", "8000"))

    def get_google_credentials(self) -> dict:
        if not self.google_sheets_credentials_json:
            raise ValueError("GOOGLE_SHEETS_CREDENTIALS_JSON no está configurada")
        try:
            return json.loads(self.google_sheets_credentials_json)
        except json.JSONDecodeError as exc:
            raise ValueError("GOOGLE_SHEETS_CREDENTIALS_JSON no es JSON válido") from exc


@lru_cache()
def get_settings() -> Settings:
    return Settings()
