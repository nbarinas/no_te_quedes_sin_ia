from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.sheets import get_sheets_client

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    sheets = get_sheets_client()
    contacts = sheets.get_contacts_for_sidebar()
    stats = {
        "pendientes": sheets.count_pending_contacts(),
        "bloqueados": len(sheets.get_blocked_phones()),
    }
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "contacts": contacts, "stats": stats}
    )


@router.get("/api/contacts")
def list_contacts():
    sheets = get_sheets_client()
    return {"contactos": sheets.get_contacts_for_sidebar()}


@router.get("/api/conversations")
def list_conversations(telefono: str = "", limite: int = 20):
    sheets = get_sheets_client()
    conversations = sheets.get_conversations(telefono=telefono if telefono else None, limite=limite)
    return {"conversaciones": conversations}


@router.get("/api/stats")
def get_stats():
    sheets = get_sheets_client()
    return {
        "pendientes": sheets.count_pending_contacts(),
        "bloqueados": len(sheets.get_blocked_phones()),
    }
