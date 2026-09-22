import json
import os
from datetime import datetime, timezone
from typing import Any, List, Optional

import gspread
from google.auth.exceptions import GoogleAuthError
from google.oauth2.service_account import Credentials

from app.config import get_settings

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SHEET_CONTACTOS = "contactos"
SHEET_CONVERSACIONES = "conversaciones"

CONTACTOS_HEADERS = ["nombre", "telefono", "estado", "fecha_envio", "notas"]
CONVERSACIONES_HEADERS = ["telefono", "tipo", "mensaje", "fecha", "agente"]


class SheetsClient:
    def __init__(self):
        self.settings = get_settings()
        self.client = self._auth()
        self.spreadsheet = self.client.open_by_key(self.settings.google_sheets_spreadsheet_id)

    def _auth(self) -> gspread.Client:
        creds_info = self.settings.get_google_credentials()
        credentials = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
        return gspread.authorize(credentials)

    def _get_or_create_sheet(self, title: str) -> gspread.Worksheet:
        try:
            return self.spreadsheet.worksheet(title)
        except gspread.WorksheetNotFound:
            sheet = self.spreadsheet.add_worksheet(title=title, rows=1000, cols=20)
            return sheet

    def ensure_headers(self):
        contactos = self._get_or_create_sheet(SHEET_CONTACTOS)
        conversaciones = self._get_or_create_sheet(SHEET_CONVERSACIONES)

        if not contactos.row_values(1):
            contactos.append_row(CONTACTOS_HEADERS)
        if not conversaciones.row_values(1):
            conversaciones.append_row(CONVERSACIONES_HEADERS)

    def get_pending_contacts(self, limit: int = 50) -> List[dict]:
        sheet = self._get_or_create_sheet(SHEET_CONTACTOS)
        records = sheet.get_all_records(expected_headers=CONTACTOS_HEADERS)
        pending = []
        for record in records:
            estado = str(record.get("estado", "")).strip().lower()
            if estado in ("", "pendiente", "no enviado"):
                pending.append(record)
            if len(pending) >= limit:
                break
        return pending

    def update_contact_status(self, telefono: str, estado: str, notas: str = ""):
        sheet = self._get_or_create_sheet(SHEET_CONTACTOS)
        records = sheet.get_all_records(expected_headers=CONTACTOS_HEADERS)
        for idx, record in enumerate(records, start=2):
            if str(record.get("telefono", "")).strip() == telefono.strip():
                sheet.update_cell(idx, CONTACTOS_HEADERS.index("estado") + 1, estado)
                sheet.update_cell(
                    idx, CONTACTOS_HEADERS.index("fecha_envio") + 1, now_iso()
                )
                if notas:
                    sheet.update_cell(idx, CONTACTOS_HEADERS.index("notas") + 1, notas)
                return True
        return False

    def add_conversation(self, telefono: str, tipo: str, mensaje: str, agente: str = "bot"):
        sheet = self._get_or_create_sheet(SHEET_CONVERSACIONES)
        sheet.append_row([telefono, tipo, mensaje, now_iso(), agente])

    def get_conversations(self, telefono: Optional[str] = None) -> List[dict]:
        sheet = self._get_or_create_sheet(SHEET_CONVERSACIONES)
        records = sheet.get_all_records(expected_headers=CONVERSACIONES_HEADERS)
        if telefono:
            records = [r for r in records if str(r.get("telefono", "")).strip() == telefono.strip()]
        return records

    def get_contact_phones(self) -> List[str]:
        sheet = self._get_or_create_sheet(SHEET_CONTACTOS)
        records = sheet.get_all_records(expected_headers=CONTACTOS_HEADERS)
        return [str(r["telefono"]).strip() for r in records if r.get("telefono")]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_sheets_client() -> SheetsClient:
    return SheetsClient()
