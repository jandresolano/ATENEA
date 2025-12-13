# whatsapp_service.py
import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import logging
from datetime import datetime

class WhatsAppService:
    def __init__(self, app=None):
        self.client = None
        self.whatsapp_number = None
        self.initialized = False
        self.mode = "no_inicializado"
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar el servicio de WhatsApp con la configuración de la app"""
        logging.info("🚀 INICIANDO INIT_APP DE WHATSAPP SERVICE")
        try:
            # Usar configuración de la app en lugar de credenciales hardcodeadas
            account_sid = app.config.get('TWILIO_ACCOUNT_SID')
            auth_token = app.config.get('TWILIO_AUTH_TOKEN')
            self.whatsapp_number = app.config.get('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
            
            logging.info("🔧 Configurando WhatsApp Service desde app.config...")
            logging.info(f"   Account SID: {account_sid}")
            logging.info(f"   Auth Token: {auth_token[:10]}..." if auth_token else "No configurado")
            logging.info(f"   WhatsApp Number: {self.whatsapp_number}")
            
            # Validar credenciales
            if not account_sid or not auth_token:
                logging.error("❌ Credenciales de Twilio no configuradas en app.config")
                self._setup_simulation_mode()
                return
            
            # Intentar inicializar Twilio
            self.client = Client(account_sid, auth_token)
            
            # Probar conexión
            try:
                account = self.client.api.accounts(account_sid).fetch()
                self.initialized = True
                self.mode = "twilio"
                logging.info("✅✅✅ TWILIO INICIALIZADO CORRECTAMENTE - MODO REAL ✅✅✅")
                
            except TwilioRestException as e:
                logging.error(f"❌ Error de Twilio: {e.code} - {e.msg}")
                self._setup_simulation_mode()
                
        except Exception as e:
            logging.error(f"❌ Error inicializando WhatsApp: {str(e)}")
            self._setup_simulation_mode()
    
    def _setup_simulation_mode(self):
        """Configurar modo simulación"""
        self.initialized = True
        self.mode = "simulación"
        logging.warning("🔄 Cambiando a MODO SIMULACIÓN")

    def enviar_mensaje(self, numero_destino, mensaje):
        """Enviar mensaje de WhatsApp"""
        if not self.initialized:
            return False, "Servicio de WhatsApp no inicializado"
        
        if self.mode == "simulación":
            return self._enviar_simulacion(numero_destino, mensaje)
        elif self.mode == "twilio":
            return self._enviar_twilio_real(numero_destino, mensaje)
        
        return False, "Modo desconocido"
    
    def _enviar_simulacion(self, numero_destino, mensaje):
        """Enviar mensaje en modo simulación"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            logging.info("=" * 50)
            logging.info(f"📱 [{timestamp}] SIMULACIÓN DE WHATSAPP")
            logging.info(f"   👤 DESTINATARIO: {numero_destino}")
            logging.info(f"   📝 MENSAJE: {mensaje}")
            logging.info(f"   ✅ SIMULACIÓN EXITOSA")
            logging.info("=" * 50)
            return True, "simulado"
        except Exception as e:
            return False, str(e)
    
    def _enviar_twilio_real(self, numero_destino, mensaje):
        """Enviar mensaje real con Twilio"""
        try:
            numero_formateado = f"whatsapp:{numero_destino}"
            message = self.client.messages.create(
                body=mensaje,
                from_=self.whatsapp_number,
                to=numero_formateado
            )
            logging.info(f"✅ Mensaje REAL enviado: {message.sid}")
            return True, message.sid
        except Exception as e:
            logging.error(f"❌ Error enviando mensaje real: {str(e)}")
            return False, str(e)

    def esta_inicializado(self):
        return self.initialized
    
    def get_mode(self):
        return self.mode

# Instancia global del servicio
whatsapp_service = WhatsAppService()