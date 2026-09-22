# Notas para agentes de código

## Propósito del proyecto

Sistema para enviar mensajes masivos de WhatsApp usando la API oficial de Meta, registrar contactos y conversaciones en Google Sheets, y responder manualmente desde un panel web.

## Cómo correr localmente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/prepare_env.py
python -m scripts.setup_sheets
uvicorn app.main:app --reload
```

## Estructura

- `app/main.py`: punto de entrada FastAPI.
- `app/config.py`: variables de entorno.
- `app/sheets.py`: integración con Google Sheets.
- `app/whatsapp.py`: integración con Meta WhatsApp Cloud API.
- `app/routes/`: endpoints de envío, webhook y dashboard.
- `app/templates/dashboard.html`: panel web simple.
- `scripts/setup_sheets.py`: crea encabezados de las hojas.
- `scripts/prepare_env.py`: genera el archivo `.env` desde el JSON de Google.
- `render.yaml`: configuración de despliegue en Render.

## Convenciones

- Usar español para nombres de variables relacionadas con el negocio.
- No subir nunca credenciales: `.env` y archivos JSON de cuentas de servicio están en `.gitignore`.
- Las variables de entorno sensibles se leen desde `app.config.get_settings()`.

## Tests básicos

Antes de commit, verificar sintaxis:

```bash
python -m compileall app scripts
```

## Despliegue

- Subir a GitHub.
- Conectar repositorio en Render.
- Configurar variables de entorno en Render.
- Configurar webhook en Meta apuntando a `https://<tu-url>/webhook`.

## Dependencias principales

- FastAPI / Uvicorn
- gspread / google-auth
- httpx
- python-dotenv
