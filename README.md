# WhatsApp Talleres de IA

Aplicación en Python + FastAPI para enviar mensajes masivos por WhatsApp usando la API oficial de Meta (WhatsApp Cloud API), guardar contactos y conversaciones en Google Sheets, y responder desde un panel web.

## Características

- Envío por lotes de 50 mensajes usando plantillas aprobadas por Meta.
- Registro de contactos con estados: pendiente, enviado, error.
- Webhook para recibir respuestas y eventos de entrega.
- Panel web para ver conversaciones y responder manualmente.
- Hoja `contactos` y hoja `conversaciones` en Google Sheets.
- Listo para desplegar en Render.

## Requisitos previos

1. Cuenta de Meta Business con un número de WhatsApp Business verificado.
2. Plantilla de mensaje aprobada en Meta con el nombre `talleres_ia_saludo`.
3. Proyecto en Google Cloud con Sheets API y Drive API habilitadas, y una cuenta de servicio.
4. Hoja de cálculo de Google Sheets compartida con el email de la cuenta de servicio.
5. Cuenta en Render (plan gratuito).

## Instalación local

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Crea un archivo `.env` basado en `.env.example` y completa tus credenciales.

```bash
cp .env.example .env
```

## Configurar Google Sheets

1. Crea una hoja de cálculo vacía en Google Sheets.
2. Ve a Google Cloud Console → APIs y servicios → Credenciales → Cuenta de servicio.
3. Descarga el JSON de la cuenta de servicio.
4. Comparte la hoja de cálculo con el email de la cuenta de servicio (Editor).
5. Convierte el JSON a una sola línea y guárdalo en `GOOGLE_SHEETS_CREDENTIALS_JSON`.

Para crear las hojas y encabezados:

```bash
python -m scripts.setup_sheets
```

También puedes usar el helper interactivo para generar el `.env`:

```bash
python scripts/prepare_env.py
```

## Configurar Meta WhatsApp Cloud API

1. Crea una app en Meta Developers.
2. Agrega el producto WhatsApp.
3. Verifica tu número de teléfono.
4. Crea una plantilla con nombre `talleres_ia_saludo` y contenido similar a:

```
Hola {{1}}. ¿Sientes que la Inteligencia Artificial avanza muy rápido y te cuesta cogerle el hilo? Estoy organizando talleres prácticos (noches y fines de semana) para aprender desde cero y sin enredos. Avísame si te cuento de qué trata.
```

5. Copia el token de acceso, el ID del número de teléfono y configúralos en `.env`.
6. Elige un `META_VERIFY_TOKEN` seguro para el webhook.

## Ejecutar localmente

```bash
uvicorn app.main:app --reload
```

Panel web: http://localhost:8000/

## Enviar un lote de prueba

Puedes hacer una petición `dry_run` para ver qué contactos se enviarían sin enviar realmente:

```bash
curl -X POST http://localhost:8000/api/send-batch \
  -H "Content-Type: application/json" \
  -d '{"limit":50,"dry_run":true}'
```

Para enviar de verdad:

```bash
curl -X POST http://localhost:8000/api/send-batch \
  -H "Content-Type: application/json" \
  -d '{"limit":50}'
```

## Desplegar en Render

1. Sube el código a GitHub.
2. En Render, crea un nuevo Web Service conectado a tu repositorio.
3. Configura las variables de entorno desde `.env` en el panel de Render.
4. Render usará `render.yaml` para el despliegue.
5. Copia la URL del servicio (por ejemplo, `https://whatsapp-talleres-ia.onrender.com`).

## Configurar el webhook en Meta

1. En el panel de tu app de Meta, ve a WhatsApp → Configuración.
2. En Webhooks, haz clic en "Configurar webhooks".
3. URL de callback: `https://tu-url-de-render.com/webhook`
4. Token de verificación: el mismo valor de `META_VERIFY_TOKEN`
5. Suscríbete al campo `messages`.

## Estructura de las hojas

### contactos

| nombre | telefono | estado | fecha_envio | notas |

### conversaciones

| telefono | tipo | mensaje | fecha | agente |

## Mantener vivo el servicio gratis de Render

El plan gratuito de Render se duerme tras 15 minutos de inactividad. Puedes usar un servicio externo como UptimeRobot o Cron-Job.org para hacer ping cada 5 minutos a `/health`.

## Licencia

Uso personal y comercial bajo tu propia responsabilidad.
