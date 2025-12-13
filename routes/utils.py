# routes/utils.py
from flask import redirect, url_for, flash, session
import smtplib
from email.mime.text import MIMEText
from database import test_db_connection

# Función para verificar autenticación y roles
def login_required(role=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                flash("Debe iniciar sesión primero", "error")
                return redirect(url_for("login"))
            
            if role and session.get('user_role') != role:
                flash("No tiene permisos para acceder a esta página", "error")
                return redirect(url_for("panel_administrador" if session.get('user_role') == 'ADMINISTRADOR' else "panel_residente"))
            
            return func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator

# --- Funciones de email ---
def enviar_codigo_verificacion(correo, codigo, app):
    try:
        msg = MIMEText(f'Su código de verificación es: {codigo}. Válido por 10 minutos.')
        msg['Subject'] = 'Código de verificación - Sistema Residencial'
        msg['From'] = app.config['MAIL_USERNAME']
        msg['To'] = correo
        
        server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        server.starttls()
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False

def enviar_codigo_recuperacion(correo, codigo, app):
    try:
        msg = MIMEText(f'Su código de recuperación es: {codigo}. Válido por 10 minutos.')
        msg['Subject'] = 'Recuperación de contraseña - Sistema Residencial'
        msg['From'] = app.config['MAIL_USERNAME']
        msg['To'] = correo
        
        server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        server.starttls()
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False

# Exportar función de test de base de datos
from database import test_db_connection