from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from app.sheets import get_sheets_client
from app.whatsapp import get_whatsapp_client

router = APIRouter()

DEFAULT_TEMPLATE = "talleres_ia_saludo"
DEFAULT_MESSAGE = (
    "Hola {nombre}. ¿Sientes que la Inteligencia Artificial avanza muy rápido "
    "y te cuesta cogerle el hilo? Estoy organizando talleres prácticos "
    "(noches y fines de semana) para aprender desde cero y sin enredos. "
    "Avísame si te cuento de qué trata."
)


class BatchRequest(BaseModel):
    limit: int = 50
    template_name: str = DEFAULT_TEMPLATE
    dry_run: bool = False


class ReplyRequest(BaseModel):
    telefono: str
    mensaje: str


@router.post("/send-batch")
async def send_batch(payload: BatchRequest):
    sheets = get_sheets_client()
    wa = get_whatsapp_client()

    pending = sheets.get_pending_contacts(limit=payload.limit)
    if not pending:
        return {"enviados": 0, "errores": 0, "detalles": []}

    results = []
    for contact in pending:
        telefono = str(contact.get("telefono", "")).strip()
        nombre = str(contact.get("nombre", "")).strip() or "amigo/a"

        if not telefono:
            results.append({"telefono": telefono, "status": "error", "error": "sin teléfono"})
            continue

        try:
            if payload.dry_run:
                results.append({"telefono": telefono, "status": "dry_run", "nombre": nombre})
                continue

            await wa.send_template(
                to=telefono,
                template_name=payload.template_name,
                language="es",
                variables=[nombre],
            )
            sheets.update_contact_status(telefono, "enviado", notas="Primer mensaje enviado")
            sheets.add_conversation(telefono, "saliente", DEFAULT_MESSAGE.format(nombre=nombre), agente="bot")
            results.append({"telefono": telefono, "status": "enviado", "nombre": nombre})
        except Exception as exc:
            sheets.update_contact_status(telefono, "error", notas=str(exc))
            results.append({"telefono": telefono, "status": "error", "error": str(exc)})

    return {
        "enviados": sum(1 for r in results if r["status"] == "enviado"),
        "errores": sum(1 for r in results if r["status"] == "error"),
        "detalles": results,
    }


@router.post("/reply")
async def reply(payload: ReplyRequest):
    sheets = get_sheets_client()
    wa = get_whatsapp_client()

    phones = sheets.get_contact_phones()
    if payload.telefono.strip() not in phones:
        raise HTTPException(status_code=404, detail="Número no encontrado en contactos")

    try:
        await wa.send_text_message(payload.telefono, payload.mensaje)
        sheets.add_conversation(payload.telefono, "saliente", payload.mensaje, agente="humano")
        return {"status": "enviado"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
