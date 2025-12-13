from flask import Flask, render_template, jsonify, session
from flask_mail import Mail, Message  
from database import init_db, db
from models import Usuario, Reserva, Reporte, GestionEspera, Evento, PrestamoParqueadero, Anuncio, Recibo, Actividad, Voluntario, Incidente, Vehiculo, InscripcionEvento
from routes.auth_routes import init_auth_routes
from routes.admin_routes import init_admin_routes
from routes.resident_routes import init_resident_routes
from routes.event_routes import init_event_routes
from routes.user_routes import init_user_routes
from routes.sorteo_routes import init_sorteo_routes
from routes.reportes_routes import init_reportes_routes
from routes.gestion_routes import init_gestion_routes
from routes.parqueadero_routes import init_parqueadero_routes
from routes.anuncios_routes import init_anuncios_routes
from routes.recibos_routes import init_recibos_routes
from routes.actividades_routes import init_actividades_routes
from routes.voluntarios_routes import init_voluntarios_routes
from routes.seguridad_routes import init_seguridad_routes
from routes.portero_routes import init_portero_routes
from routes.vehiculos_routes import init_vehiculos_routes
from routes.recordatorios_routes import init_recordatorios_routes
from whatsapp_service import whatsapp_service
import logging
import os
import sys

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# -----------------------------------------------------
# Configuración de la aplicación
# -----------------------------------------------------
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback_key_segura')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql+mysqlconnector://root@127.0.0.1:3306/sistema_residencial')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# -----------------------------------------------------
# Configuración de email
# -----------------------------------------------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME', '')

# -----------------------------------------------------
# Configuración de WhatsApp (Twilio)
# -----------------------------------------------------
app.config['TWILIO_ACCOUNT_SID'] = os.environ.get('TWILIO_ACCOUNT_SID', '')
app.config['TWILIO_AUTH_TOKEN'] = os.environ.get('TWILIO_AUTH_TOKEN', '')
app.config['TWILIO_WHATSAPP_NUMBER'] = os.environ.get('TWILIO_WHATSAPP_NUMBER', '')

# -----------------------------------------------------
# Inicializar servicios
# -----------------------------------------------------

# Inicializar base de datos
init_db(app)

# Inicializar servicio WhatsApp
whatsapp_service.init_app(app)
logging.info("✅ Servicio WhatsApp inicializado")

# Verificar y configurar Flask-Mail
try:
    mail = Mail(app)
    FLASK_MAIL_AVAILABLE = True
    logging.info("✅ Flask-Mail configurado correctamente")
except Exception as e:
    mail = None
    FLASK_MAIL_AVAILABLE = False
    logging.warning(f"⚠️  Flask-Mail no disponible: {e}")

# -----------------------------------------------------
# Ruta de inicio mejorada
# -----------------------------------------------------
@app.route("/")
def inicio():
    eventos_proximos = Reserva.query.filter(
        Reserva.FECHA_HORA >= db.func.now(),
        Reserva.ESTADO == 'ACTIVO'
    ).order_by(Reserva.FECHA_HORA).limit(5).all()
    
    # Inscripciones del usuario actual (si está logueado)
    mis_inscripciones = []
    if 'user_id' in session:
        mis_inscripciones = [insc.ID_RESERVA for insc in InscripcionEvento.query.filter_by(
            ID_USUARIO=session['user_id']
        ).all()]
    
    return render_template("inicio.html", 
                        eventos_proximos=eventos_proximos,
                        mis_inscripciones=mis_inscripciones)

# -----------------------------------------------------
# Inicialización segura de todas las rutas
# -----------------------------------------------------
def init_routes_safely():
    routes_config = [
        ('auth_routes', 'init_auth_routes', None),
        ('admin_routes', 'init_admin_routes', None),
        ('resident_routes', 'init_resident_routes', None),
        ('event_routes', 'init_event_routes', None),
        ('user_routes', 'init_user_routes', None),
        ('sorteo_routes', 'init_sorteo_routes', None),
        ('reportes_routes', 'init_reportes_routes', None),
        ('gestion_routes', 'init_gestion_routes', None),
        ('parqueadero_routes', 'init_parqueadero_routes', None),
        ('anuncios_routes', 'init_anuncios_routes', None),
        ('recibos_routes', 'init_recibos_routes', None),
        ('actividades_routes', 'init_actividades_routes', None),
        ('voluntarios_routes', 'init_voluntarios_routes', None),
        ('seguridad_routes', 'init_seguridad_routes', None),
        ('portero_routes', 'init_portero_routes', None),
        ('vehiculos_routes', 'init_vehiculos_routes', None),
        ('recordatorios_routes', 'init_recordatorios_routes', mail)
    ]
    
    for route_module, init_func, extra_param in routes_config:
        try:
            module = __import__(f'routes.{route_module}', fromlist=[init_func])
            init_function = getattr(module, init_func)
            
            if extra_param is not None:
                init_function(app, extra_param)
            else:
                init_function(app)
                
            logging.info(f"✅ {route_module} inicializado correctamente")
        except ImportError as e:
            logging.warning(f"⚠️  No se pudo inicializar {route_module}: {e}")
        except Exception as e:
            logging.error(f"❌ Error inicializando {route_module}: {e}")

# Inicializar todas las rutas
init_routes_safely()

# -----------------------------------------------------
# API de eventos próximos (para carrusel)
# -----------------------------------------------------
@app.route('/api/eventos_proximos')
def api_eventos_proximos():
    eventos = Reserva.query.filter(
        Reserva.FECHA_HORA >= db.func.now(),
        Reserva.ESTADO == 'ACTIVO'
    ).order_by(Reserva.FECHA_HORA).limit(10).all()
    
    eventos_data = []
    for evento in eventos:
        eventos_data.append({
            'id': evento.ID_RESERVA,
            'nombre': evento.NOMBRE,
            'fecha': evento.FECHA_HORA.strftime('%d/%m/%Y %H:%M'),
            'descripcion': evento.DESCRIPCION,
            'tipo': evento.TIPO,
            'clase': evento.CLASE
        })
    
    return jsonify(eventos_data)

# -----------------------------------------------------
# Ruta de prueba para verificar que la app funciona
# -----------------------------------------------------
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'OK',
        'message': 'Sistema Residencial funcionando correctamente',
        'database': 'Conectado' if db.session.bind else 'Desconectado',
        'flask_mail': 'Disponible' if FLASK_MAIL_AVAILABLE else 'No disponible',
        'whatsapp_service': 'Inicializado'
    })

# -----------------------------------------------------
# Ruta de prueba de email
# -----------------------------------------------------
@app.route('/test_email')
def test_email():
    if not FLASK_MAIL_AVAILABLE or not mail:
        return "❌ Flask-Mail no disponible"
    
    try:
        msg = Message(
            subject="Prueba de correo - Sistema Residencial",
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=['jsolanofigueredo@gmail.com']
        )
        msg.body = "Este es un correo de prueba del Sistema Residencial"
        mail.send(msg)
        return "✅ Correo de prueba enviado exitosamente"
    except Exception as e:
        return f"❌ Error enviando correo: {str(e)}"

# -----------------------------------------------------
# Manejo de errores
# -----------------------------------------------------
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# -----------------------------------------------------
# Ejecución de la aplicación
# -----------------------------------------------------
if __name__ == "__main__":
    print("🚀 Iniciando Sistema Residencial...")
    print(f"🔗 URL de base de datos: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"📧 Correo configurado: {app.config['MAIL_USERNAME']}")
    print(f"📨 Flask-Mail disponible: {FLASK_MAIL_AVAILABLE}")
    print(f"📱 Servicio WhatsApp: Inicializado")
    app.run(debug=True, host='0.0.0.0', port=5000)