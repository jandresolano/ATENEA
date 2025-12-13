# routes/user_routes.py
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from database import db
from models import Usuario, Reserva, InscripcionEvento, RecordatorioEvento, Sorteo
from werkzeug.security import generate_password_hash
from sqlalchemy import or_
from .utils import login_required

def init_user_routes(app):
    
    def validar_apartamento(torre, apartamento):
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

    @app.route("/gestion_usuarios")
    @login_required('ADMINISTRADOR')
    def gestion_usuarios():
        search_query = request.args.get('search', '').strip()
        
        # Consulta base
        query = Usuario.query
        
        # Aplicar filtro de búsqueda si existe
        if search_query:
            query = query.filter(
                or_(
                    Usuario.NOMBRE.ilike(f'%{search_query}%'),
                    Usuario.APELLIDO.ilike(f'%{search_query}%'),
                    Usuario.CORREO.ilike(f'%{search_query}%'),
                    Usuario.TELEFONO.ilike(f'%{search_query}%'),
                    Usuario.APARTAMENTO.ilike(f'%{search_query}%'),
                    Usuario.TORRE.ilike(f'%{search_query}%'),
                    Usuario.ROL.ilike(f'%{search_query}%')
                )
            )
        
        # Obtener todos los usuarios (para estadísticas)
        todos_usuarios = query.order_by(Usuario.ESTADO, Usuario.NOMBRE).all()
        
        # Separar por estados
        usuarios_pendientes = [u for u in todos_usuarios if u.ESTADO == 'PENDIENTE']
        usuarios_activos = [u for u in todos_usuarios if u.ESTADO == 'ACTIVO']
        usuarios_inactivos = [u for u in todos_usuarios if u.ESTADO == 'INACTIVO']
        
        # Estadísticas
        stats = {
            'total': len(todos_usuarios),
            'pendientes': len(usuarios_pendientes),
            'activos': len(usuarios_activos),
            'inactivos': len(usuarios_inactivos),
            'administradores': len([u for u in todos_usuarios if u.ROL == 'ADMINISTRADOR']),
            'residentes': len([u for u in todos_usuarios if u.ROL == 'RESIDENTE']),
            'porteros': len([u for u in todos_usuarios if u.ROL == 'PORTERO'])
        }
        
        return render_template("gestion_usuarios.html", 
                             pendientes=usuarios_pendientes,
                             activos=usuarios_activos,
                             inactivos=usuarios_inactivos,
                             todos_usuarios=todos_usuarios,
                             search_query=search_query,
                             stats=stats,
                             user_name=session.get('user_name'),
                             user_role=session.get('user_role'))

    @app.route("/crear_usuario", methods=["GET", "POST"])
    @login_required('ADMINISTRADOR')
    def crear_usuario():
        if request.method == "POST":
            try:
                # Obtener datos del formulario
                nombre = request.form["nombre"]
                apellido = request.form["apellido"]
                correo = request.form["correo"]
                telefono = request.form["telefono"]
                rol = request.form["rol"]
                estado = request.form["estado"]
                contrasena = request.form["contrasena"]
                apartamento = request.form.get("apartamento", "").strip()
                torre = request.form.get("torre", "").strip()
                
                # Validar campos para residentes
                if rol == 'RESIDENTE':
                    if not apartamento or not torre:
                        flash("Torre y apartamento son obligatorios para residentes", "error")
                        return render_template("crear_usuario.html")
                    
                    # Validar formato de apartamento
                    es_valido, mensaje = validar_apartamento(torre, apartamento)
                    if not es_valido:
                        flash(mensaje, "error")
                        return render_template("crear_usuario.html")
                
                # Verificar si el correo ya existe
                usuario_existente = Usuario.query.filter_by(CORREO=correo).first()
                if usuario_existente:
                    flash("El correo electrónico ya está registrado", "error")
                    return render_template("crear_usuario.html")
                
                # Para residentes, verificar si el apartamento ya está ocupado
                if rol == 'RESIDENTE':
                    apartamento_existente = Usuario.query.filter_by(
                        TORRE=torre, 
                        APARTAMENTO=apartamento,
                        ROL='RESIDENTE',
                        ESTADO='ACTIVO'
                    ).first()
                    
                    if apartamento_existente:
                        flash(f"El apartamento {apartamento} de la torre {torre} ya está ocupado", "error")
                        return render_template("crear_usuario.html")
                
                # Crear nuevo usuario
                nuevo_usuario = Usuario(
                    NOMBRE=nombre,
                    APELLIDO=apellido,
                    CORREO=correo,
                    TELEFONO=telefono,
                    ROL=rol,
                    ESTADO=estado,
                    CONTRASENA=generate_password_hash(contrasena)
                )
                
                # Solo agregar torre y apartamento para residentes
                if rol == 'RESIDENTE':
                    nuevo_usuario.TORRE = torre
                    nuevo_usuario.APARTAMENTO = apartamento
                
                db.session.add(nuevo_usuario)
                db.session.commit()
                
                flash("Usuario creado exitosamente", "exito")
                return redirect(url_for("gestion_usuarios"))
                
            except Exception as e:
                db.session.rollback()
                flash(f"Error al crear el usuario: {str(e)}", "error")
                return render_template("crear_usuario.html")
        
        return render_template("crear_usuario.html")

    @app.route("/aprobar_usuario/<int:user_id>")
    @login_required('ADMINISTRADOR')
    def aprobar_usuario(user_id):
        try:
            usuario = Usuario.query.get(user_id)
            if usuario and usuario.ESTADO == 'PENDIENTE':
                usuario.ESTADO = 'ACTIVO'
                db.session.commit()
                flash(f"Usuario {usuario.NOMBRE} {usuario.APELLIDO} aprobado exitosamente", "exito")
            else:
                flash("Usuario no encontrado o ya no está pendiente", "error")
        except Exception as e:
            db.session.rollback()
            flash(f"Error al aprobar usuario: {str(e)}", "error")
        
        return redirect(url_for("gestion_usuarios"))

    @app.route("/rechazar_usuario/<int:user_id>")
    @login_required('ADMINISTRADOR')
    def rechazar_usuario(user_id):
        try:
            usuario = Usuario.query.get(user_id)
            if usuario and usuario.ESTADO == 'PENDIENTE':
                usuario.ESTADO = 'INACTIVO'
                db.session.commit()
                flash(f"Usuario {usuario.NOMBRE} {usuario.APELLIDO} rechazado", "info")
            else:
                flash("Usuario no encontrado o ya no está pendiente", "error")
        except Exception as e:
            db.session.rollback()
            flash(f"Error al rechazar usuario: {str(e)}", "error")
        
        return redirect(url_for("gestion_usuarios"))

    @app.route("/editar_usuario/<int:user_id>", methods=["GET", "POST"])
    @login_required('ADMINISTRADOR')
    def editar_usuario(user_id):
        usuario = Usuario.query.get_or_404(user_id)

        if request.method == "POST":
            try:
                usuario.NOMBRE = request.form["nombre"]
                usuario.APELLIDO = request.form["apellido"]
                usuario.CORREO = request.form["correo"]
                usuario.TELEFONO = request.form["telefono"]
                usuario.ROL = request.form["rol"]
                usuario.ESTADO = request.form["estado"]
                
                # Validar apartamento para residentes
                if usuario.ROL == "RESIDENTE":
                    apartamento = request.form.get("apartamento", "").strip()
                    torre = request.form.get("torre", "").strip()
                    
                    if not apartamento or not torre:
                        flash("Torre y apartamento son obligatorios para residentes", "error")
                        return render_template("editar_usuario.html", usuario=usuario)
                    
                    es_valido, mensaje = validar_apartamento(torre, apartamento)
                    if not es_valido:
                        flash(mensaje, "error")
                        return render_template("editar_usuario.html", usuario=usuario)
                    
                    # Verificar si el apartamento está ocupado por otro residente activo
                    apartamento_existente = Usuario.query.filter(
                        Usuario.TORRE == torre,
                        Usuario.APARTAMENTO == apartamento,
                        Usuario.ROL == 'RESIDENTE',
                        Usuario.ESTADO == 'ACTIVO',
                        Usuario.ID_USUARIO != user_id
                    ).first()
                    
                    if apartamento_existente:
                        flash(f"El apartamento {apartamento} de la torre {torre} ya está ocupado", "error")
                        return render_template("editar_usuario.html", usuario=usuario)
                    
                    usuario.APARTAMENTO = apartamento
                    usuario.TORRE = torre

                db.session.commit()
                flash("Usuario actualizado correctamente", "exito")
                return redirect(url_for("gestion_usuarios"))
            except Exception as e:
                db.session.rollback()
                flash(f"Error al actualizar usuario: {str(e)}", "error")

        return render_template("editar_usuario.html", usuario=usuario)

    @app.route("/eliminar_usuario/<int:user_id>", methods=["POST"])
    @login_required('ADMINISTRADOR')
    def eliminar_usuario(user_id):
        try:
            usuario = Usuario.query.get_or_404(user_id)
            
            # Verificar que no sea el usuario actual
            if usuario.ID_USUARIO == session.get('user_id'):
                flash("No puedes eliminar tu propio usuario", "error")
                return redirect(url_for("gestion_usuarios"))
            
            # Primero eliminar registros relacionados en otras tablas
            Sorteo.query.filter_by(ID_USUARIO=user_id).delete()
            InscripcionEvento.query.filter_by(ID_USUARIO=user_id).delete()
            RecordatorioEvento.query.filter_by(ID_USUARIO=user_id).delete()
            Reserva.query.filter_by(ID_USUARIO=user_id).delete()
            
            db.session.delete(usuario)
            db.session.commit()
            
            flash("Usuario eliminado correctamente", "exito")
        except Exception as e:
            db.session.rollback()
            flash(f"Error al eliminar usuario: {str(e)}", "error")

        return redirect(url_for("gestion_usuarios"))