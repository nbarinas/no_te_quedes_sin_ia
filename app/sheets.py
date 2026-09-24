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

CONTACTOS_HEADERS = ["nombre", "telefono", "estado", "fecha_envio", "notas", "bloqueado"]
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

        self._ensure_sheet_headers(contactos, CONTACTOS_HEADERS)
        self._ensure_sheet_headers(conversaciones, CONVERSACIONES_HEADERS)

    def _ensure_sheet_headers(self, sheet: gspread.Worksheet, expected_headers: List[str]):
        current = sheet.row_values(1)
        if not current:
            sheet.append_row(expected_headers)
            return

        # Si faltan columnas, agregarlas al final
        missing = [h for h in expected_headers if h not in current]
        if missing:
            next_col = len(current) + 1
            for idx, header in enumerate(missing):
                sheet.update_cell(1, next_col + idx, header)

    def _get_contact_records(self) -> List[dict]:
        sheet = self._get_or_create_sheet(SHEET_CONTACTOS)
        try:
            return sheet.get_all_records(expected_headers=CONTACTOS_HEADERS)
        except gspread.GSpreadException:
            # Fallback por si los encabezados no coinciden exactamente
            return sheet.get_all_records()

    def get_pending_contacts(self, limit: int = 50) -> List[dict]:
        records = self._get_contact_records()
        pending = []
        for record in records:
            estado = str(record.get("estado", "")).strip().lower()
            bloqueado = str(record.get("bloqueado", "")).strip().lower()
            if bloqueado in ("si", "yes", "true", "1"):
                continue
            if estado in ("", "pendiente", "no enviado"):
                pending.append(record)
            if len(pending) >= limit:
                break
        return pending

    def get_blocked_phones(self) -> List[str]:
        records = self._get_contact_records()
        blocked = []
        for record in records:
            bloqueado = str(record.get("bloqueado", "")).strip().lower()
            if bloqueado in ("si", "yes", "true", "1"):
                blocked.append(str(record.get("telefono", "")).strip())
        return blocked

    def set_block_status(self, telefono: str, bloqueado: bool) -> bool:
        sheet = self._get_or_create_sheet(SHEET_CONTACTOS)
        records = self._get_contact_records()
        col_idx = self._header_index(sheet, "bloqueado")
        for idx, record in enumerate(records, start=2):
            if str(record.get("telefono", "")).strip() == telefono.strip():
                value = "si" if bloqueado else "no"
                sheet.update_cell(idx, col_idx, value)
                return True
        return False

    def _header_index(self, sheet: gspread.Worksheet, header: str) -> int:
        headers = [h.strip().lower() for h in sheet.row_values(1)]
        return headers.index(header.lower()) + 1

    def update_contact_status(self, telefono: str, estado: str, notas: str = ""):
        sheet = self._get_or_create_sheet(SHEET_CONTACTOS)
        records = self._get_contact_records()
        for idx, record in enumerate(records, start=2):
            if str(record.get("telefono", "")).strip() == telefono.strip():
                sheet.update_cell(idx, self._header_index(sheet, "estado"), estado)
                sheet.update_cell(idx, self._header_index(sheet, "fecha_envio"), now_iso())
                if notas:
                    sheet.update_cell(idx, self._header_index(sheet, "notas"), notas)
                return True
        return False

    def add_conversation(self, telefono: str, tipo: str, mensaje: str, agente: str = "bot"):
        sheet = self._get_or_create_sheet(SHEET_CONVERSACIONES)
        sheet.append_row([telefono, tipo, mensaje, now_iso(), agente])

    def get_conversations(self, telefono: Optional[str] = None, limite: int = 20) -> List[dict]:
        sheet = self._get_or_create_sheet(SHEET_CONVERSACIONES)
        records = sheet.get_all_records(expected_headers=CONVERSACIONES_HEADERS)
        if telefono:
            records = [r for r in records if str(r.get("telefono", "")).strip() == telefono.strip()]
        records.sort(key=lambda r: r.get("fecha", ""), reverse=True)
        return records[:limite]

    def get_contact_phones(self) -> List[str]:
        records = self._get_contact_records()
        return [str(r["telefono"]).strip() for r in records if r.get("telefono")]

    def get_contacts_for_sidebar(self) -> List[dict]:
        contacts = self._get_contact_records()
        conversations = self.get_conversations(limite=1000)
        last_by_phone = {}
        for c in conversations:
            phone = str(c.get("telefono", "")).strip()
            if phone and phone not in last_by_phone:
                last_by_phone[phone] = c

        result = []
        for record in contacts:
            phone = str(record.get("telefono", "")).strip()
            if not phone:
                continue
            bloqueado = str(record.get("bloqueado", "")).strip().lower() in ("si", "yes", "true", "1")
            last = last_by_phone.get(phone, {})
            result.append({
                "telefono": phone,
                "nombre": str(record.get("nombre", "")).strip() or phone,
                "bloqueado": bloqueado,
                "estado": str(record.get("estado", "")).strip().lower(),
                "ultimo_mensaje": str(last.get("mensaje", ""))[:60],
                "ultima_fecha": last.get("fecha", ""),
            })
        return result

    def count_pending_contacts(self) -> int:
        records = self._get_contact_records()
        count = 0
        for record in records:
            estado = str(record.get("estado", "")).strip().lower()
            bloqueado = str(record.get("bloqueado", "")).strip().lower()
            if bloqueado in ("si", "yes", "true", "1"):
                continue
            if estado in ("", "pendiente", "no enviado"):
                count += 1
        return count


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_sheets_client() -> SheetsClient:
    return SheetsClient()
