"""
Genera el archivo .env a partir de service_account.json y datos que introduces.
Uso:
    python scripts/prepare_env.py
"""
import json
import os


def main():
    json_path = "service_account.json"
    if not os.path.exists(json_path):
        print(f"No se encontró {json_path}. Descarga la clave JSON de Google Cloud y guárdala aquí.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        credentials = json.load(f)

    spreadsheet_id = input("Pega el ID de tu hoja de Google Sheets: ").strip()

    print("Ahora necesito los datos de Meta. Si aún no los tienes, deja en blanco y los completas luego.")
    meta_token = input("META_ACCESS_TOKEN: ").strip()
    meta_phone_id = input("META_PHONE_NUMBER_ID: ").strip()
    meta_verify_token = input("META_VERIFY_TOKEN (elige uno seguro para el webhook): ").strip()
    meta_app_secret = input("META_APP_SECRET: ").strip()
    app_secret = input("APP_SECRET_KEY (deja en blanco para generar uno aleatorio): ").strip()

    if not app_secret:
        import secrets
        app_secret = secrets.token_urlsafe(32)

    env_content = f"""# Meta WhatsApp Cloud API
META_ACCESS_TOKEN={meta_token}
META_PHONE_NUMBER_ID={meta_phone_id}
META_VERIFY_TOKEN={meta_verify_token}
META_APP_SECRET={meta_app_secret}

# Google Sheets
GOOGLE_SHEETS_CREDENTIALS_JSON={json.dumps(credentials, separators=(',', ':'))}
GOOGLE_SHEETS_SPREADSHEET_ID={spreadsheet_id}

# App
APP_SECRET_KEY={app_secret}
"""

    with open(".env", "w", encoding="utf-8") as f:
        f.write(env_content)

    print("\n✅ Archivo .env creado correctamente.")
    print("Recuerda: .env está en .gitignore y NO se sube a GitHub.")


if __name__ == "__main__":
    main()
