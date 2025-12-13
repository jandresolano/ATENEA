# routes/admin_routes.py
from flask import render_template, session, request, flash, jsonify
from .utils import login_required
from models import Usuario, db
import logging

# Importar el servicio de WhatsApp
try:
    from whatsapp_service import whatsapp_service
    WHATSAPP_AVAILABLE = True
    logging.info("✅ WhatsApp service importado correctamente")
except ImportError as e:
    WHATSAPP_AVAILABLE = False
    logging.error(f"❌ Error importando WhatsApp service: {e}")

def init_admin_routes(app):
    @app.route("/panel_administrador")
    @login_required('ADMINISTRADOR')
    def panel_administrador():
        return render_template("panel_administrador.html", 
                             user_name=session.get('user_name'),
                             user_role=session.get('user_role'))
    
    @app.route('/admin/notificaciones/whatsapp')
    @login_required('ADMINISTRADOR')
    def admin_notificaciones_whatsapp():
        """Panel para enviar notificaciones por WhatsApp"""
        # Obtener estado del servicio WhatsApp
        whatsapp_status = {
            "available": WHATSAPP_AVAILABLE,
            "initialized": whatsapp_service.esta_inicializado() if WHATSAPP_AVAILABLE else False,
            "mode": whatsapp_service.get_mode() if WHATSAPP_AVAILABLE else "unavailable",
            "status": "active" if (WHATSAPP_AVAILABLE and whatsapp_service.esta_inicializado()) else "inactive"
        }
        
        return render_template('admin_notificaciones_whatsapp.html',
                             user_name=session.get('user_name'),
                             user_role=session.get('user_role'),
                             whatsapp_status=whatsapp_status)
    
    @app.route('/admin/api/usuarios/telefonos')
    @login_required('ADMINISTRADOR')
    def api_usuarios_telefonos():
        """API para obtener usuarios con teléfonos"""
        try:
            usuarios = Usuario.query.filter(
                Usuario.telefono.isnot(None),
                Usuario.telefono != ''
            ).all()
            
            usuarios_data = [{
                'id': u.id,
                'nombre': f"{u.nombre} {u.apellido}" if u.apellido else u.nombre,
                'telefono': u.telefono,
                'rol': u.rol
            } for u in usuarios]
            
            logging.info(f"📞 Obtenidos {len(usuarios_data)} usuarios con teléfono")
            return jsonify(usuarios_data)
            
        except Exception as e:
            logging.error(f"❌ Error obteniendo usuarios: {e}")
            return jsonify([])
    
    @app.route('/admin/enviar/whatsapp', methods=['POST'])
    @login_required('ADMINISTRADOR')
    def enviar_notificacion_whatsapp():
        """Endpoint para enviar notificaciones por WhatsApp"""
        try:
            # Verificar disponibilidad del servicio
            if not WHATSAPP_AVAILABLE:
                return jsonify({
                    'success': False, 
                    'message': '❌ Servicio de WhatsApp no disponible. Verifica el archivo whatsapp_service.py'
                })
            
            if not whatsapp_service.esta_inicializado():
                return jsonify({
                    'success': False, 
                    'message': '❌ Servicio de WhatsApp no inicializado'
                })
            
            data = request.get_json()
            tipo_destino = data.get('tipo_destino')
            mensaje = data.get('mensaje')
            numero_personalizado = data.get('numero_personalizado')
            
            # Validaciones básicas
            if not mensaje or not mensaje.strip():
                return jsonify({'success': False, 'message': '❌ El mensaje no puede estar vacío'})
            
            if not tipo_destino:
                return jsonify({'success': False, 'message': '❌ Selecciona un tipo de destinatario'})
            
            # Obtener destinatarios
            destinatarios = []
            if tipo_destino == 'todos':
                # Enviar a todos los residentes con teléfono
                residentes = Usuario.query.filter_by(rol='residente').all()
                destinatarios = [r for r in residentes if r.telefono]
                logging.info(f"📞 Enviando a {len(destinatarios)} residentes con teléfono")
                
            elif tipo_destino == 'personalizado' and numero_personalizado:
                # Validar formato del número personalizado
                if not numero_personalizado.startswith('+'):
                    return jsonify({
                        'success': False, 
                        'message': '❌ El número debe empezar con + (ej: +573001234567)'
                    })
                
                destinatarios = [type('Obj', (), {
                    'telefono': numero_personalizado.strip(), 
                    'nombre': 'Destinatario Personalizado',
                    'id': 'personalizado'
                })()]
                logging.info(f"📞 Enviando a número personalizado: {numero_personalizado}")
            else:
                return jsonify({
                    'success': False, 
                    'message': '❌ Selecciona un destinatario válido'
                })
            
            # Verificar que hay destinatarios
            if not destinatarios:
                return jsonify({
                    'success': False, 
                    'message': '❌ No hay destinatarios disponibles con los criterios seleccionados'
                })
            
            # Enviar mensajes
            enviados = 0
            errores = []
            
            for destinatario in destinatarios:
                if destinatario.telefono:
                    success, resultado = whatsapp_service.enviar_mensaje(
                        destinatario.telefono, 
                        mensaje.strip()
                    )
                    if success:
                        enviados += 1
                        logging.info(f"✅ Mensaje enviado a {destinatario.telefono}")
                    else:
                        nombre = getattr(destinatario, 'nombre', 'Destinatario')
                        error_msg = f"{nombre}: {resultado}"
                        errores.append(error_msg)
                        logging.error(f"❌ Error enviando a {destinatario.telefono}: {resultado}")
            
            # Preparar respuesta
            modo_actual = whatsapp_service.get_mode()
            
            if enviados > 0:
                if modo_actual == "twilio":
                    message = f'✅ {enviados} mensajes de WhatsApp enviados exitosamente'
                else:
                    message = f'✅ {enviados} mensajes simulados exitosamente (Modo Simulación)'
            else:
                message = '❌ No se pudo enviar ningún mensaje'
                
            if errores:
                message += f'. Se encontraron {len(errores)} errores'
            
            resultado = {
                'success': enviados > 0,
                'enviados': enviados,
                'errores': errores,
                'message': message,
                'mode': modo_actual,
                'total_destinatarios': len(destinatarios)
            }
                
            return jsonify(resultado)
            
        except Exception as e:
            logging.error(f"❌ Error enviando notificación WhatsApp: {str(e)}")
            return jsonify({
                'success': False, 
                'message': f'❌ Error al enviar notificaciones: {str(e)}'
            })