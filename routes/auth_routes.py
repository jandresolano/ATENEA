from flask import render_template, request, redirect, url_for, flash, session
from database import db
from models import Usuario
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random
import re
from .utils import enviar_codigo_verificacion, enviar_codigo_recuperacion, test_db_connection

# Diccionarios temporales para almacenar códigos
verification_codes = {}
recovery_codes = {}

def init_auth_routes(app):
    
    def validar_apartamento_registro(torre, apartamento):
        """Valida que el apartamento sea válido para la torre"""
        try:
            # Validar torre (1-22)
            torre_num = int(torre)
            if torre_num < 1 or torre_num > 22:
                return False, "La torre debe estar entre 1 y 22"
            
            # Validar apartamento (formato: 101-604)
            if len(apartamento) != 3:
                return False, "El apartamento debe tener 3 dígitos (ej: 101)"
            
            piso = int(apartamento[0])
            numero_apto = int(apartamento[1:])
            
            # Validar piso (1-6) y número de apartamento (1-4 por piso)
            if piso < 1 or piso > 6:
                return False, "El piso debe estar entre 1 y 6"
            
            if numero_apto < 1 or numero_apto > 4:
                return False, "El número de apartamento debe estar entre 1 y 4"
            
            return True, "Válido"
            
        except ValueError:
            return False, "Formato inválido. Use números (ej: torre: 1, apartamento: 101)"

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            usuario = request.form["usuario"].lower()
            password = request.form["password"]
            
            try:
                user = Usuario.query.filter_by(CORREO=usuario).first()
                
                if user and check_password_hash(user.CONTRASENA, password):
                    if user.ESTADO == 'ACTIVO':
                        # Si es administrador, requerir verificación en dos pasos
                        if user.ROL == 'ADMINISTRADOR':
                            # Generar código de verificación
                            codigo = str(random.randint(100000, 999999))
                            expiration = datetime.now() + timedelta(minutes=10)
                            
                            # Guardar código temporalmente
                            verification_codes[user.ID_USUARIO] = {
                                'codigo': codigo,
                                'expira': expiration
                            }
                            
                            # Enviar código por email
                            if enviar_codigo_verificacion(user.CORREO, codigo, app):
                                session['pending_admin'] = user.ID_USUARIO
                                flash("Se ha enviado un código de verificación a su correo", "info")
                                return redirect(url_for("verificar_codigo"))
                            else:
                                flash("Error al enviar el código de verificación. Verifique la configuración de correo.", "error")
                                return redirect(url_for("login"))
                        
                        # Para otros roles (RESIDENTE, PORTERO), iniciar sesión directamente
                        session['user_id'] = user.ID_USUARIO
                        session['user_name'] = user.NOMBRE
                        session['user_role'] = user.ROL
                        
                        flash("Inicio de sesión exitoso", "exito")
                        
                        # Redirección mejorada para todos los roles
                        if user.ROL == 'ADMINISTRADOR':
                            return redirect(url_for("panel_administrador"))
                        elif user.ROL == 'PORTERO':
                            return redirect(url_for("portero.panel_portero")) 
                        else:
                            return redirect(url_for("panel_residente"))
                    elif user.ESTADO == 'PENDIENTE':
                        flash("Su cuenta está pendiente de aprobación por el administrador", "error")
                    else:
                        flash("Su cuenta está inactiva. Contacte al administrador.", "error")
                else:
                    flash("Usuario o contraseña incorrectos", "error")
                    return redirect(url_for("login"))
                    
            except Exception as e:
                flash(f"Error de conexión: {str(e)}", "error")
                return redirect(url_for("login"))

        db_status = test_db_connection()
        return render_template("login.html", db_connected=db_status)

    @app.route("/verificar_codigo", methods=["GET", "POST"])
    def verificar_codigo():
        if 'pending_admin' not in session:
            flash("Acceso denegado. Inicie sesión primero.", "error")
            return redirect(url_for("login"))
        
        user_id = session['pending_admin']
        user = Usuario.query.get(user_id)
        
        if not user:
            session.pop('pending_admin', None)
            flash("Usuario no encontrado.", "error")
            return redirect(url_for("login"))

        if request.method == "POST":
            codigo_ingresado = request.form["codigo"]
            
            # Verificar si el código existe y no ha expirado
            if (user_id in verification_codes and 
                verification_codes[user_id]['codigo'] == codigo_ingresado and
                datetime.now() < verification_codes[user_id]['expira']):
                
                # Código válido, iniciar sesión
                session['user_id'] = user.ID_USUARIO
                session['user_name'] = user.NOMBRE
                session['user_role'] = user.ROL
                
                # Limpiar código de verificación
                del verification_codes[user_id]
                session.pop('pending_admin', None)
                
                flash("Verificación exitosa. Sesión iniciada.", "exito")

                # Redirección mejorada para todos los roles
                if user.ROL == 'ADMINISTRADOR':
                    return redirect(url_for("panel_administrador"))
                elif user.ROL == 'PORTERO':
                    return redirect(url_for("portero.panel_portero"))
                else:
                    return redirect(url_for("panel_residente"))
            else:
                flash("Código de verificación inválido o expirado", "error")
                return render_template("verificar_codigo.html", correo=user.CORREO)
        
        return render_template("verificar_codigo.html", correo=user.CORREO)

    @app.route("/registro", methods=["GET", "POST"])
    def registro_residente():
        if request.method == "POST":
            try:
                # Obtener datos del formulario
                nombre = request.form["nombre"].strip()
                apellido = request.form["apellido"].strip()
                correo = request.form["correo"].strip().lower()
                telefono = request.form["telefono"].strip()
                apartamento = request.form["apartamento"].strip()
                torre = request.form["torre"].strip()
                contrasena = request.form["contrasena"]
                confirmar_contrasena = request.form["confirmar_contrasena"]
                
                # Validaciones básicas
                if not all([nombre, apellido, correo, telefono, apartamento, torre, contrasena]):
                    flash("Todos los campos son obligatorios", "error")
                    return render_template("registro_residente.html")
                
                # Validar formato de apartamento y torre
                es_valido, mensaje = validar_apartamento_registro(torre, apartamento)
                if not es_valido:
                    flash(mensaje, "error")
                    return render_template("registro_residente.html")
                
                if contrasena != confirmar_contrasena:
                    flash("Las contraseñas no coinciden", "error")
                    return render_template("registro_residente.html")
                
                if len(contrasena) < 6:
                    flash("La contraseña debe tener al menos 6 caracteres", "error")
                    return render_template("registro_residente.html")
                
                if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
                    flash("Por favor ingrese un correo electrónico válido", "error")
                    return render_template("registro_residente.html")
                
                # Verificar si el correo ya existe
                usuario_existente = Usuario.query.filter_by(CORREO=correo).first()
                if usuario_existente:
                    flash("El correo electrónico ya está registrado", "error")
                    return render_template("registro_residente.html")
                
                # Verificar si el apartamento ya está ocupado por otro residente
                apartamento_existente = Usuario.query.filter_by(
                    TORRE=torre, 
                    APARTAMENTO=apartamento,
                    ROL='RESIDENTE'
                ).first()
                
                if apartamento_existente:
                    flash(f"El apartamento {apartamento} de la torre {torre} ya está registrado", "error")
                    return render_template("registro_residente.html")
                
                # Crear nuevo usuario residente
                nuevo_usuario = Usuario(
                    NOMBRE=nombre,
                    APELLIDO=apellido,
                    CORREO=correo,
                    TELEFONO=telefono,
                    APARTAMENTO=apartamento,
                    TORRE=torre,
                    ROL='RESIDENTE',
                    ESTADO='PENDIENTE',
                    CONTRASENA=generate_password_hash(contrasena)
                )
                
                db.session.add(nuevo_usuario)
                db.session.commit()
                
                flash("Registro exitoso. Su cuenta está pendiente de aprobación por el administrador.", "exito")
                return redirect(url_for("login"))
                
            except Exception as e:
                db.session.rollback()
                flash(f"Error al registrar: {str(e)}", "error")
                return render_template("registro_residente.html")
        
        # Generar listas de torres y apartamentos para el template
        torres = list(range(1, 23))
        apartamentos = []
        for piso in range(1, 7):
            for apto in range(1, 5):
                numero_apto = f"{piso}{apto:02d}"
                apartamentos.append({
                    'valor': numero_apto,
                    'texto': f"{numero_apto} (Piso {piso}, Apto {apto})"
                })
        
        return render_template("registro_residente.html", 
                             torres=torres, 
                             apartamentos=apartamentos)

    @app.route("/recuperar_clave", methods=["GET", "POST"])
    def recuperar_clave():
        if request.method == "POST":
            correo = request.form["correo"].lower()
            
            try:
                user = Usuario.query.filter_by(CORREO=correo).first()
                
                if user:
                    # Generar código de recuperación
                    codigo = str(random.randint(100000, 999999))
                    expiration = datetime.now() + timedelta(minutes=10)
                    
                    # Guardar código temporalmente
                    recovery_codes[user.ID_USUARIO] = {
                        'codigo': codigo,
                        'expira': expiration
                    }
                    
                    # Enviar código por email
                    if enviar_codigo_recuperacion(user.CORREO, codigo, app):
                        session['pending_recovery'] = user.ID_USUARIO
                        flash("Se ha enviado un código de recuperación a su correo", "info")
                        return redirect(url_for("verificar_codigo_recuperacion"))
                    else:
                        flash("Error al enviar el código de recuperación", "error")
                        return redirect(url_for("recuperar_clave"))
                else:
                    flash("No existe una cuenta con ese correo electrónico", "error")
                    return redirect(url_for("recuperar_clave"))
                    
            except Exception as e:
                flash(f"Error: {str(e)}", "error")
                return redirect(url_for("recuperar_clave"))
        
        return render_template("recuperar_clave.html")

    @app.route("/verificar_codigo_recuperacion", methods=["GET", "POST"])
    def verificar_codigo_recuperacion():
        if 'pending_recovery' not in session:
            flash("Acceso denegado", "error")
            return redirect(url_for("login"))
        
        user_id = session['pending_recovery']
        user = Usuario.query.get(user_id)
        
        if not user:
            session.pop('pending_recovery', None)
            flash("Usuario no encontrado", "error")
            return redirect(url_for("login"))

        if request.method == "POST":
            codigo_ingresado = request.form["codigo"]
            
            # Verificar si el código existe y no ha expirado
            if (user_id in recovery_codes and 
                recovery_codes[user_id]['codigo'] == codigo_ingresado and
                datetime.now() < recovery_codes[user_id]['expira']):
                
                # Código válido, redirigir a restablecer contraseña
                session['allow_password_reset'] = user_id
                del recovery_codes[user_id]
                return redirect(url_for("restablecer_clave"))
            else:
                flash("Código de recuperación inválido o expirado", "error")
        
        return render_template("verificar_codigo_recuperacion.html", correo=user.CORREO)

    @app.route("/restablecer_clave", methods=["GET", "POST"])
    def restablecer_clave():
        if 'allow_password_reset' not in session:
            flash("Acceso denegado", "error")
            return redirect(url_for("login"))
        
        user_id = session['allow_password_reset']
        user = Usuario.query.get(user_id)
        
        if not user:
            session.pop('allow_password_reset', None)
            flash("Usuario no encontrado", "error")
            return redirect(url_for("login"))

        if request.method == "POST":
            nueva_clave = request.form["nueva_clave"]
            confirmar_clave = request.form["confirmar_clave"]
            
            if nueva_clave != confirmar_clave:
                flash("Las contraseñas no coinciden", "error")
                return render_template("restablecer_clave.html")
            
            if len(nueva_clave) < 6:
                flash("La contraseña debe tener al menos 6 caracteres", "error")
                return render_template("restablecer_clave.html")
            
            # Actualizar contraseña
            user.CONTRASENA = generate_password_hash(nueva_clave)
            db.session.commit()
            
            session.pop('allow_password_reset', None)
            flash("Contraseña restablecida exitosamente", "exito")
            return redirect(url_for("login"))
        
        return render_template("restablecer_clave.html")

    @app.route("/logout")
    def logout():
        # Limpiar completamente la sesión
        session.clear()
        
        # Agregar headers para prevenir cache (mejora del compañero)
        response = redirect(url_for('inicio'))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        flash('Sesión cerrada exitosamente', 'success')
        return response