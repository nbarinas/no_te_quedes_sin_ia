from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routes import send, webhook, dashboard

app = FastAPI(title="WhatsApp Talleres IA")

templates = Jinja2Templates(directory="app/templates")

app.include_router(send.router, prefix="/api", tags=["Envío"])
app.include_router(webhook.router, prefix="", tags=["Webhook"])
app.include_router(dashboard.router, prefix="", tags=["Dashboard"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
