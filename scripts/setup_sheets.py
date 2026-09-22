"""
Script para crear las hojas y encabezados iniciales en Google Sheets.
Uso:
    python scripts/setup_sheets.py
Requiere que GOOGLE_SHEETS_CREDENTIALS_JSON y GOOGLE_SHEETS_SPREADSHEET_ID
estén configuradas en el archivo .env o como variables de entorno.
"""
from app.sheets import get_sheets_client


def main():
    client = get_sheets_client()
    client.ensure_headers()
    print("Hojas creadas/verificadas correctamente.")
    print("- contactos")
    print("- conversaciones")


if __name__ == "__main__":
    main()
