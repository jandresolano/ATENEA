import os

# -----------------------------------------------------
# Configuración general
# -----------------------------------------------------
SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback_key_segura')

SQLALCHEMY_DATABASE_URI = os.environ.get(
    'DATABASE_URL',
    'mysql+mysqlconnector://root@127.0.0.1:3306/sistema_residencial'
)

SQLALCHEMY_TRACK_MODIFICATIONS = False

# -----------------------------------------------------
# Configuración de correo (Flask-Mail)
# -----------------------------------------------------
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
MAIL_DEFAULT_SENDER = MAIL_USERNAME

# -----------------------------------------------------
# Configuración de WhatsApp (Twilio)
# -----------------------------------------------------
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_WHATSAPP_NUMBER = os.environ.get('TWILIO_WHATSAPP_NUMBER', '')

# -----------------------------------------------------
# Configuración de ejecución
# -----------------------------------------------------
DEBUG = True
HOST = '0.0.0.0'
PORT = 5000
