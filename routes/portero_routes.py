from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from models import db, Usuario, Paquete
from datetime import datetime
import logging
from sqlalchemy import func

# Crear Blueprint para rutas de portero
portero_bp = Blueprint('portero', __name__)

@portero_bp.route('/panel_portero')
def panel_portero():
    """Panel principal del portero"""
    try:
        # Estadísticas
        total_paquetes = Paquete.query.count()
        paquetes_pendientes = Paquete.query.filter_by(estado='recibido').count()
        paquetes_notificados = Paquete.query.filter_by(estado='notificado').count()
        paquetes_entregados_hoy = Paquete.query.filter(
            Paquete.estado == 'entregado',
            func.date(Paquete.fecha_entrega) == func.current_date()
        ).count()
        
        # Paquetes recientes (últimos 10)
        paquetes_recientes = Paquete.query.order_by(Paquete.fecha_ingreso.desc()).limit(10).all()
        
        return render_template('panel_portero.html',
                            total_paquetes=total_paquetes,
                            paquetes_pendientes=paquetes_pendientes,
                            paquetes_notificados=paquetes_notificados,
                            paquetes_entregados=paquetes_entregados_hoy,
                            paquetes_recientes=paquetes_recientes)
    except Exception as e:
        logging.error(f"Error en panel_portero: {str(e)}")
        flash('Error al cargar el panel', 'error')
        return render_template('panel_portero.html')

@portero_bp.route('/registrar_paquete', methods=['GET', 'POST'])
def registrar_paquete():
    """Registrar nuevo paquete"""
    if request.method == 'POST':
        try:
            torre = request.form.get('torre')
            apartamento = request.form.get('apartamento')
            descripcion = request.form.get('descripcion')
            remitente = request.form.get('remitente')
            numero_seguimiento = request.form.get('numero_seguimiento')
            observaciones = request.form.get('observaciones')
            
            # Buscar residente
            residente = Usuario.query.filter_by(
                TORRE=torre,
                APARTAMENTO=apartamento,
                ESTADO='ACTIVO'
            ).first()
            
            # Crear paquete
            nuevo_paquete = Paquete(
                residente_id=residente.ID_USUARIO if residente else None,
                torre=torre,
                apartamento=apartamento,
                descripcion=descripcion,
                remitente=remitente,
                numero_seguimiento=numero_seguimiento,
                observaciones=observaciones,
                estado='recibido'
            )
            
            db.session.add(nuevo_paquete)
            db.session.commit()
            
            flash('Paquete registrado exitosamente', 'success')
            return redirect(url_for('portero.panel_portero'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error al registrar paquete: {str(e)}")
            flash('Error al registrar el paquete', 'error')
    
    return render_template('registrar_paquete.html')

@portero_bp.route('/listar_paquetes')
def listar_paquetes():
    """Listar todos los paquetes con filtros"""
    estado = request.args.get('estado', 'all')
    
    query = Paquete.query
    
    if estado != 'all':
        query = query.filter_by(estado=estado)
    
    paquetes = query.order_by(Paquete.fecha_ingreso.desc()).all()
    
    # Estadísticas para los filtros
    total_paquetes = Paquete.query.count()
    paquetes_recibidos = Paquete.query.filter_by(estado='recibido').count()
    paquetes_notificados_count = Paquete.query.filter_by(estado='notificado').count()
    paquetes_entregados_count = Paquete.query.filter_by(estado='entregado').count()
    
    return render_template('listar_paquetes.html', 
                         paquetes=paquetes, 
                         estado_actual=estado,
                         total_paquetes=total_paquetes,
                         paquetes_recibidos=paquetes_recibidos,
                         paquetes_notificados=paquetes_notificados_count,
                         paquetes_entregados=paquetes_entregados_count)

@portero_bp.route('/paquetes_pendientes')
def paquetes_pendientes():
    """Paquetes pendientes de notificación"""
    paquetes = Paquete.query.filter_by(estado='recibido')\
                           .order_by(Paquete.fecha_ingreso.asc()).all()
    return render_template('paquetes_pendientes.html', paquetes=paquetes)

@portero_bp.route('/notificar_paquete/<int:paquete_id>')
def notificar_paquete(paquete_id):
    """Notificar paquete por CORREO electrónico"""
    try:
        paquete = Paquete.query.get_or_404(paquete_id)
        
        # Buscar residente manualmente
        if paquete.residente_id:
            residente = Usuario.query.get(paquete.residente_id)
        else:
            residente = Usuario.query.filter_by(
                TORRE=paquete.torre,
                APARTAMENTO=paquete.apartamento,
                ESTADO='ACTIVO'
            ).first()
        
        if not residente:
            flash('No se encontró información del residente', 'error')
            return redirect(url_for('portero.listar_paquetes'))
        
        # Enviar notificación por CORREO
        if residente.CORREO:
            if enviar_notificacion_correo(residente, paquete):
                paquete.notificado_correo = True
                paquete.estado = 'notificado'
                paquete.fecha_notificacion = datetime.now()
                db.session.commit()
                flash('Notificación por correo enviada exitosamente', 'success')
            else:
                flash('Error al enviar notificación por correo', 'error')
        else:
            flash('El residente no tiene correo electrónico registrado', 'warning')
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error al notificar paquete: {str(e)}")
        flash('Error al notificar el paquete', 'error')
    
    return redirect(url_for('portero.listar_paquetes'))

@portero_bp.route('/marcar_entregado/<int:paquete_id>')
def marcar_entregado(paquete_id):
    """Marcar paquete como entregado"""
    try:
        paquete = Paquete.query.get_or_404(paquete_id)
        paquete.estado = 'entregado'
        paquete.fecha_entrega = datetime.now()
        
        db.session.commit()
        
        flash('Paquete marcado como entregado', 'success')
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error al marcar paquete como entregado: {str(e)}")
        flash('Error al actualizar el paquete', 'error')
    
    return redirect(url_for('portero.listar_paquetes'))

@portero_bp.route('/buscar_residente')
def buscar_residente():
    """Buscar residente por torre y apartamento (para AJAX)"""
    torre = request.args.get('torre')
    apartamento = request.args.get('apartamento')
    
    residente = Usuario.query.filter_by(
        TORRE=torre,
        APARTAMENTO=apartamento,
        ESTADO='ACTIVO'
    ).first()
    
    if residente:
        return jsonify({
            'existe': True,
            'nombre': f"{residente.NOMBRE} {residente.APELLIDO}",
            'correo': residente.CORREO,
            'telefono': residente.TELEFONO
        })
    else:
        return jsonify({'existe': False})

def enviar_notificacion_correo(residente, paquete):
    """Enviar notificación por CORREO electrónico"""
    try:
        from flask_mail import Mail, Message
        
        # Inicializar Flask-Mail
        mail = Mail(current_app)
        
        subject = "📦 Tiene un paquete en la portería - Conjunto Residencial Alameda"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #0056b3; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 10px 10px; }}
                .info-box {{ background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #0056b3; }}
                .footer {{ text-align: center; margin-top: 20px; padding: 20px; color: #666; font-size: 0.9em; }}
                .highlight {{ color: #0056b3; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Conjunto Residencial Alameda</h1>
                    <p>Sistema de Notificaciones de Portería</p>
                </div>
                
                <div class="content">
                    <h2>¡Tiene un paquete en portería!</h2>
                    <p>Estimado(a) <span class="highlight">{residente.NOMBRE} {residente.APELLIDO}</span>,</p>
                    
                    <div class="info-box">
                        <h3>📦 Información del paquete:</h3>
                        <p><strong>🏠 Torre/Apartamento:</strong> {paquete.torre}-{paquete.apartamento}</p>
                        <p><strong>📋 Descripción:</strong> {paquete.descripcion}</p>
                        <p><strong>📦 Remitente:</strong> {paquete.remitente or 'No especificado'}</p>
                        <p><strong>🔢 N° Seguimiento:</strong> {paquete.numero_seguimiento or 'N/A'}</p>
                        <p><strong>📅 Fecha de recepción:</strong> {paquete.fecha_ingreso.strftime('%d/%m/%Y a las %H:%M')}</p>
                    </div>
                    
                    <h3>📍 Instrucciones para recoger:</h3>
                    <p>Puede pasar por portería a recoger su paquete presentando su documento de identidad.</p>
                    
                    <h3>🕒 Horario de atención:</h3>
                    <ul>
                        <li><strong>Lunes a Domingo:</strong> 7:00 AM - 9:00 PM</li>
                    </ul>
                    
                    <p style="background: #fff3cd; padding: 10px; border-radius: 5px; border-left: 4px solid #ffc107;">
                        <strong>💡 Importante:</strong> Los paquetes se conservan por un máximo de 15 días.
                    </p>
                </div>
                
                <div class="footer">
                    <p>Atentamente,<br>
                    <strong>Equipo de Portería</strong><br>
                    Conjunto Residencial Alameda el Porvenir<br>
                    📞 Contacto: Portería principal</p>
                    <p><em>Este es un mensaje automático, por favor no responda a este correo.</em></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Crear y enviar el mensaje
        msg = Message(
            subject=subject,
            recipients=[residente.CORREO],
            html=html_body,
            sender=('Conjunto Residencial Alameda', current_app.config.get('MAIL_USERNAME'))
        )
        
        mail.send(msg)
        logging.info(f"✅ Notificación por correo enviada a {residente.CORREO}")
        return True
        
    except Exception as e:
        logging.error(f"❌ Error enviando correo a {residente.CORREO}: {str(e)}")
        return False

def init_portero_routes(app):
    """Registrar rutas de portero en la aplicación"""
    app.register_blueprint(portero_bp)