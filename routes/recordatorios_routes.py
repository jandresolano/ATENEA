# routes/recordatorios_routes.py
from flask import render_template, request, redirect, url_for, flash, session
from models import Reserva, InscripcionEvento, RecordatorioEvento, Usuario
from database import db
from datetime import datetime, timedelta

# Import seguro de login_required
try:
    from middleware import login_required
except ImportError:
    from functools import wraps
    def login_required(role=None):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if 'user_id' not in session:
                    flash('Debes iniciar sesión para acceder a esta página', 'error')
                    return redirect(url_for('login'))
                if role and session.get('user_role') != role:
                    flash('No tienes permisos para acceder a esta página', 'error')
                    return redirect(url_for("inicio"))
                return f(*args, **kwargs)
            return decorated_function
        return decorator

def init_recordatorios_routes(app, mail_instance):
    
    def cambiar_correo_remitente(nuevo_correo, nueva_contraseña, nombre_remitente="Administración Conjunto Residencial"):
        """Cambia temporalmente la configuración de correo"""
        if mail_instance:
            # Guardar configuración original
            original_config = {
                'username': app.config.get('MAIL_USERNAME'),
                'password': app.config.get('MAIL_PASSWORD'),
                'sender': app.config.get('MAIL_DEFAULT_SENDER')
            }
            
            # Cambiar a nueva configuración
            app.config['MAIL_USERNAME'] = nuevo_correo
            app.config['MAIL_PASSWORD'] = nueva_contraseña
            app.config['MAIL_DEFAULT_SENDER'] = (nombre_remitente, nuevo_correo)
            
            # Reconfigurar Flask-Mail
            mail_instance.init_app(app)
            return True, original_config
        return False, None
    
    def restaurar_correo_original(original_config):
        """Restaura la configuración original de correo"""
        if original_config and mail_instance:
            app.config['MAIL_USERNAME'] = original_config['username']
            app.config['MAIL_PASSWORD'] = original_config['password']
            app.config['MAIL_DEFAULT_SENDER'] = original_config['sender']
            mail_instance.init_app(app)
    
    @app.route('/enviar_recordatorios_correo')
    @login_required('ADMINISTRADOR')
    def enviar_recordatorios_correo():
        print("🔔 Iniciando envío de recordatorios...")
        
        # Obtener información del admin que envía
        admin_id = session.get('user_id')
        admin = Usuario.query.get(admin_id)
        admin_nombre = admin.NOMBRE if admin else "Administración"
        
        # CORREOS DISPONIBLES - ACTUALIZA LAS CONTRASEÑAS
        correos_disponibles = {
            'jsolanofigueredo@gmail.com': 'gcut einu gejh bqoq'  # Este ya funciona
            # 'santiagopa0717@gmail.com': 'contraseña_app_santiago'  # Comentado hasta que tengas la contraseña
        }
        
        # Buscar eventos para recordatorios (lógica más flexible)
        ahora = datetime.now()
        limite_tiempo = ahora + timedelta(hours=24)
        
        print(f"⏰ Buscando eventos entre {ahora} y {limite_tiempo}")
        
        # BUSCAR EVENTOS MÁS FLEXIBLE - incluir diferentes estados y rangos de tiempo
        eventos_proximos = Reserva.query.filter(
            Reserva.FECHA_HORA.between(ahora, limite_tiempo)
        ).all()
        
        # Si no hay eventos en 24h, buscar en 48h
        if not eventos_proximos:
            limite_tiempo = ahora + timedelta(hours=48)
            eventos_proximos = Reserva.query.filter(
                Reserva.FECHA_HORA.between(ahora, limite_tiempo)
            ).all()
            print(f"🔍 Ampliando búsqueda a 48 horas. Eventos encontrados: {len(eventos_proximos)}")
        
        print(f"📅 Eventos próximos encontrados: {len(eventos_proximos)}")
        
        if not eventos_proximos:
            flash('ℹ️ No hay eventos programados para las próximas 48 horas', 'info')
            return redirect(url_for('listar_eventos'))
        
        # Mostrar información de eventos encontrados
        for evento in eventos_proximos:
            inscripciones = InscripcionEvento.query.filter_by(ID_RESERVA=evento.ID_RESERVA).count()
            print(f"   📋 Evento: {evento.NOMBRE} - Fecha: {evento.FECHA_HORA} - Estado: {evento.ESTADO} - Inscritos: {inscripciones}")
        
        # Intentar con cada correo hasta que uno funcione
        correo_exitoso = None
        config_original = None
        
        for correo, contraseña in correos_disponibles.items():
            print(f"🔄 Intentando configurar correo: {correo}")
            
            success, config_original = cambiar_correo_remitente(correo, contraseña, admin_nombre)
            if success:
                try:
                    # Probar el correo
                    from flask_mail import Message
                    msg_prueba = Message(
                        subject="Prueba - Sistema Recordatorios",
                        sender=app.config['MAIL_DEFAULT_SENDER'],
                        recipients=[correo]  # Enviarse a sí mismo
                    )
                    msg_prueba.body = "Prueba de configuración de correo."
                    mail_instance.send(msg_prueba)
                    
                    correo_exitoso = correo
                    print(f"✅ Correo {correo} configurado correctamente")
                    break
                    
                except Exception as e:
                    print(f"❌ Error con correo {correo}: {str(e)}")
        
        if not correo_exitoso:
            if config_original:
                restaurar_correo_original(config_original)
            flash('❌ No se pudo configurar ningún correo para enviar recordatorios', 'error')
            return redirect(url_for('listar_eventos'))
        
        print(f"✅ Usando correo: {correo_exitoso}")
        
        # PROCESAR ENVÍO DE RECORDATORIOS
        enviados = 0
        errores = 0
        total_procesados = 0
        
        for evento in eventos_proximos:
            print(f"🎯 Procesando evento: {evento.NOMBRE} (ID: {evento.ID_RESERVA})")
            
            # Obtener usuarios inscritos
            inscripciones = InscripcionEvento.query.filter_by(ID_RESERVA=evento.ID_RESERVA).all()
            print(f"   👥 Inscripciones encontradas: {len(inscripciones)}")
            
            for inscripcion in inscripciones:
                total_procesados += 1
                usuario = Usuario.query.get(inscripcion.ID_USUARIO)
                if not usuario:
                    print(f"   ❌ Usuario no encontrado para ID: {inscripcion.ID_USUARIO}")
                    errores += 1
                    continue
                
                if not usuario.CORREO or '@' not in usuario.CORREO:
                    print(f"   ❌ Usuario {usuario.NOMBRE} no tiene correo válido: {usuario.CORREO}")
                    errores += 1
                    continue
                
                print(f"   📨 Procesando: {usuario.NOMBRE} ({usuario.CORREO})")
                
                # Verificar si ya se envió recordatorio (evitar duplicados)
                recordatorio_existente = RecordatorioEvento.query.filter_by(
                    ID_RESERVA=evento.ID_RESERVA,
                    ID_USUARIO=usuario.ID_USUARIO
                ).first()
                
                if recordatorio_existente:
                    print(f"   ⏭️  Recordatorio ya enviado el {recordatorio_existente.FECHA_ENVIO}, saltando...")
                    continue
                
                # Crear registro de recordatorio
                recordatorio = RecordatorioEvento(
                    ID_RESERVA=evento.ID_RESERVA,
                    ID_USUARIO=usuario.ID_USUARIO,
                    FECHA_ENVIO=datetime.now(),
                    ESTADO='PENDIENTE'
                )
                
                # Intentar enviar email
                try:
                    from flask_mail import Message
                    
                    msg = Message(
                        subject=f"🔔 Recordatorio: {evento.NOMBRE}",
                        sender=app.config['MAIL_DEFAULT_SENDER'],
                        recipients=[usuario.CORREO],
                        reply_to=correo_exitoso
                    )
                    
                    # Email en texto plano
                    msg.body = f"""
Hola {usuario.NOMBRE},

Recordatorio de tu participación en:

EVENTO: {evento.NOMBRE}
FECHA: {evento.FECHA_HORA.strftime('%d/%m/%Y a las %H:%M')}
DESCRIPCIÓN: {evento.DESCRIPCION}

¡Esperamos contar con tu participación!

Saludos,
{admin_nombre}
Conjunto Residencial Alameda del Porvenir II
                    """
                    
                    mail_instance.send(msg)
                    recordatorio.ESTADO = 'ENVIADO'
                    enviados += 1
                    print(f"   ✅ Enviado a: {usuario.CORREO}")
                    
                except Exception as e:
                    recordatorio.ESTADO = 'ERROR'
                    errores += 1
                    print(f"   ❌ Error enviando a {usuario.CORREO}: {str(e)}")
                
                db.session.add(recordatorio)
        
        # Guardar en base de datos
        try:
            db.session.commit()
            print(f"💾 Guardado en BD - Total procesados: {total_procesados}, Enviados: {enviados}, Errores: {errores}")
            
            # Mensaje al usuario
            if enviados > 0:
                flash(f'✅ Se enviaron {enviados} recordatorios desde {correo_exitoso}', 'success')
            elif total_procesados > 0:
                flash(f'⚠️  Procesados {total_procesados} inscripciones pero no se enviaron correos nuevos', 'info')
            else:
                flash('ℹ️  No había inscripciones pendientes de recordatorio', 'info')
                
        except Exception as e:
            db.session.rollback()
            flash('Error al guardar en base de datos', 'error')
            print(f"❌ Error en commit: {str(e)}")
        
        # Restaurar configuración original
        if config_original:
            restaurar_correo_original(config_original)
        
        return redirect(url_for('listar_eventos'))

    # Ruta de diagnóstico
    @app.route('/diagnostico_recordatorios')
    @login_required('ADMINISTRADOR')
    def diagnostico_recordatorios():
        """Página de diagnóstico para ver el estado actual"""
        ahora = datetime.now()
        
        # Eventos próximos
        eventos_24h = Reserva.query.filter(
            Reserva.FECHA_HORA.between(ahora, ahora + timedelta(hours=24))
        ).all()
        
        eventos_48h = Reserva.query.filter(
            Reserva.FECHA_HORA.between(ahora, ahora + timedelta(hours=48))
        ).all()
        
        # Todas las inscripciones
        todas_inscripciones = db.session.query(
            InscripcionEvento,
            Reserva.NOMBRE.label('evento_nombre'),
            Reserva.FECHA_HORA,
            Usuario.NOMBRE.label('usuario_nombre'),
            Usuario.CORREO
        ).join(Reserva, InscripcionEvento.ID_RESERVA == Reserva.ID_RESERVA
        ).join(Usuario, InscripcionEvento.ID_USUARIO == Usuario.ID_USUARIO
        ).all()
        
        # Recordatorios existentes
        recordatorios = RecordatorioEvento.query.all()
        
        return render_template('diagnostico_recordatorios.html',
                            eventos_24h=eventos_24h,
                            eventos_48h=eventos_48h,
                            todas_inscripciones=todas_inscripciones,
                            recordatorios=recordatorios)

    # Ruta para listar recordatorios
    @app.route('/listar_recordatorios')
    @login_required('ADMINISTRADOR')
    def listar_recordatorios_view():

        from sqlalchemy.orm import aliased
        
        usuario_alias = aliased(Usuario)
        reserva_alias = aliased(Reserva)
        
        recordatorios = db.session.query(
            RecordatorioEvento,
            usuario_alias.NOMBRE.label('nombre_usuario'),
            usuario_alias.CORREO.label('correo_usuario'),
            reserva_alias.NOMBRE.label('nombre_evento'),
            reserva_alias.FECHA_HORA.label('fecha_evento')
        ).join(usuario_alias, RecordatorioEvento.ID_USUARIO == usuario_alias.ID_USUARIO
        ).join(reserva_alias, RecordatorioEvento.ID_RESERVA == reserva_alias.ID_RESERVA
        ).order_by(RecordatorioEvento.FECHA_ENVIO.desc()
        ).all()
        
        return render_template('listar_recordatorios.html', recordatorios=recordatorios)