from fastapi_mail import ConnectionConfig
import os

# Configuración de correo - usar variables de entorno
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", "correo@gmail.com"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", "contraseña"),
    MAIL_FROM=os.getenv("MAIL_FROM", "correo@gmail.com"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)