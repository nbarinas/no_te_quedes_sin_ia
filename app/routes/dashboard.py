from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.sheets import get_sheets_client

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    sheets = get_sheets_client()
    phones = sheets.get_contact_phones()
    return templates.TemplateResponse("dashboard.html", {"request": request, "phones": phones})


@router.get("/api/conversations")
def list_conversations(telefono: str = ""):
    sheets = get_sheets_client()
    conversations = sheets.get_conversations(telefono=telefono if telefono else None)
    return {"conversaciones": conversations}
