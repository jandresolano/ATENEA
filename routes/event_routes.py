from flask import render_template, request, redirect, url_for, flash, session
from database import db
from models import Reserva, InscripcionEvento, RecordatorioEvento
from datetime import datetime, timedelta
from .utils import login_required

def init_event_routes(app):
    # --- RUTAS PÚBLICAS/MIXTAS DE EVENTOS ---
    @app.route("/eventos")
    def listar_eventos():
        eventos = Reserva.query.all()
        
        # Verificar inscripciones del usuario actual si está logueado
        inscripciones = {}
        if 'user_id' in session:
            # Obtener todas las inscripciones del usuario actual
            user_inscripciones = InscripcionEvento.query.filter_by(
                ID_USUARIO=session.get('user_id')
            ).all()
            
            # Crear un diccionario con los IDs de eventos a los que está inscrito
            inscripciones = {insc.ID_RESERVA: True for insc in user_inscripciones}
        
        return render_template("eventos.html", 
                             eventos=eventos, 
                             inscripciones=inscripciones)

    # --- RUTA ÚNICA PARA CREAR EVENTO ---
    @app.route("/eventos/crear", methods=["GET", "POST"])
    @login_required('ADMINISTRADOR')
    def crear_evento():
        if request.method == "POST":
            nombre = request.form.get("nombre", "").strip()
            descripcion = request.form.get("descripcion", "").strip()
            fecha_hora_str = request.form.get("fecha_hora")

            # Validar campos vacíos
            if not nombre or not descripcion or not fecha_hora_str:
                flash("Todos los campos son obligatorios", "error")
                return render_template("crear_evento.html")

            try:
                fecha_hora = datetime.strptime(fecha_hora_str, "%Y-%m-%dT%H:%M")
            except ValueError:
                flash("Formato de fecha no válido", "error")
                return render_template("crear_evento.html")

            # Validar que la fecha no sea pasada
            if fecha_hora <= datetime.now():
                flash("No puedes crear eventos con fechas pasadas", "error")
                return render_template("crear_evento.html")

            nuevo_evento = Reserva(
                ID_USUARIO=session.get('user_id'),
                NOMBRE=nombre,
                DESCRIPCION=descripcion,
                FECHA_HORA=fecha_hora,
                ESTADO="ACTIVO",
                TIPO="PUBLICO",
                CLASE="FRECUENTE"
            )

            try:
                db.session.add(nuevo_evento)
                db.session.commit()
                flash("Evento creado exitosamente", "success")
                return redirect(url_for("listar_eventos"))
            except Exception as e:
                db.session.rollback()
                flash(f"Error al crear el evento: {str(e)}", "error")
                return render_template("crear_evento.html")

        return render_template("crear_evento.html")

    @app.route("/eventos/editar/<int:id>", methods=["GET", "POST"])
    @login_required('ADMINISTRADOR')
    def editar_evento(id):
        evento = Reserva.query.get_or_404(id)

        if request.method == "POST":
            nombre = request.form.get("nombre", "").strip()
            descripcion = request.form.get("descripcion", "").strip()
            fecha_hora_str = request.form.get("fecha_hora")
            estado = request.form.get("estado")

            # Validaciones básicas
            if not nombre or not descripcion or not fecha_hora_str:
                flash("Todos los campos son obligatorios", "error")
                return render_template("editar_evento.html", evento=evento)

            try:
                nueva_fecha = datetime.strptime(fecha_hora_str, "%Y-%m-%dT%H:%M")
            except ValueError:
                flash("Formato de fecha inválido", "error")
                return render_template("editar_evento.html", evento=evento)

            # No permitir cambiar a fecha anterior si el evento aún está activo
            if nueva_fecha < datetime.now() and evento.ESTADO == "ACTIVO":
                flash("No puedes asignar una fecha anterior para un evento activo", "error")
                return render_template("editar_evento.html", evento=evento)

            # Actualizar campos
            evento.NOMBRE = nombre
            evento.DESCRIPCION = descripcion
            evento.FECHA_HORA = nueva_fecha
            evento.ESTADO = estado or evento.ESTADO

            try:
                db.session.commit()
                flash("Evento actualizado correctamente", "success")
                return redirect(url_for("listar_eventos"))
            except Exception as e:
                db.session.rollback()
                flash(f"Error al actualizar el evento: {str(e)}", "error")
                return render_template("editar_evento.html", evento=evento)

        return render_template("editar_evento.html", evento=evento)

    @app.route("/eventos/eliminar/<int:id>")
    @login_required('ADMINISTRADOR')
    def eliminar_evento(id):
        evento = Reserva.query.get_or_404(id)
        
        try:
            # Eliminar inscripciones y recordatorios relacionados primero
            InscripcionEvento.query.filter_by(ID_RESERVA=id).delete()
            RecordatorioEvento.query.filter_by(ID_RESERVA=id).delete()
            
            db.session.delete(evento)
            db.session.commit()
            flash("Evento eliminado exitosamente", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error al eliminar el evento: {str(e)}", "error")
        
        return redirect(url_for("listar_eventos"))

    @app.route("/eventos/cancelar/<int:id>")
    @login_required('ADMINISTRADOR')
    def cancelar_evento(id):
        evento = Reserva.query.get_or_404(id)
        evento.ESTADO = "CANCELADO"
        
        try:
            db.session.commit()
            flash("Evento cancelado", "warning")
        except Exception as e:
            db.session.rollback()
            flash(f"Error al cancelar el evento: {str(e)}", "error")
            
        return redirect(url_for("listar_eventos"))

    # --- RUTAS DE RESIDENTE PARA EVENTOS ---
    @app.route("/inscribirse_evento/<int:id>")
    def inscribirse_evento(id):
        user_id = session.get("user_id")

        if not user_id:
            flash("Debes iniciar sesión para inscribirte", "error")
            return redirect(url_for("login"))

        # Verificar que el evento existe y está activo
        evento = Reserva.query.get(id)
        if not evento:
            flash("El evento no existe", "error")
            return redirect(url_for("panel_residente"))
            
        if evento.ESTADO != "ACTIVO":
            flash("No puedes inscribirte a un evento cancelado o finalizado", "error")
            return redirect(url_for("panel_residente"))

        inscripcion = InscripcionEvento.query.filter_by(
            ID_RESERVA=id,
            ID_USUARIO=user_id
        ).first()

        if inscripcion:
            flash("Ya estás inscrito en este evento", "info")
        else:
            nueva_inscripcion = InscripcionEvento(ID_RESERVA=id, ID_USUARIO=user_id)
            try:
                db.session.add(nueva_inscripcion)
                db.session.commit()
                flash("Te has inscrito al evento exitosamente", "success")
            except Exception as e:
                db.session.rollback()
                flash("Error al inscribirse en el evento", "error")

        return redirect(url_for("panel_residente"))

    @app.route("/desinscribirse_evento/<int:id>")
    def desinscribirse_evento(id):
        user_id = session.get("user_id")

        inscripcion = InscripcionEvento.query.filter_by(
            ID_RESERVA=id,
            ID_USUARIO=user_id
        ).first()

        if inscripcion:
            try:
                db.session.delete(inscripcion)
                db.session.commit()
                flash("Te has desinscrito del evento", "success")
            except Exception as e:
                db.session.rollback()
                flash("Error al desinscribirse del evento", "error")
        else:
            flash("No estabas inscrito en este evento", "info")

        return redirect(url_for("panel_residente"))

    # --- RUTAS DE RECORDATORIOS (ADMIN) ---
    @app.route("/recordatorios")
    @login_required('ADMINISTRADOR')
    def listar_recordatorios():
        recordatorios = RecordatorioEvento.query.all()
        return render_template("recordatorios.html", recordatorios=recordatorios)

    @app.route("/eventos/enviar_recordatorios")
    @login_required('ADMINISTRADOR')
    def enviar_recordatorios():
        ahora = datetime.now()
        proximos_eventos = Reserva.query.filter(
            Reserva.FECHA_HORA.between(ahora, ahora + timedelta(days=1)),
            Reserva.ESTADO == "ACTIVO"
        ).all()

        recordatorios_creados = 0
        
        try:
            for evento in proximos_eventos:
                inscripciones = InscripcionEvento.query.filter_by(ID_RESERVA=evento.ID_RESERVA).all()
                for inscripcion in inscripciones:
                    # Verificar si ya existe un recordatorio para evitar duplicados
                    recordatorio_existente = RecordatorioEvento.query.filter_by(
                        ID_RESERVA=evento.ID_RESERVA,
                        ID_USUARIO=inscripcion.ID_USUARIO
                    ).first()
                    
                    if not recordatorio_existente:
                        recordatorio = RecordatorioEvento(
                            ID_RESERVA=evento.ID_RESERVA,
                            ID_USUARIO=inscripcion.ID_USUARIO,
                            FECHA_ENVIO=datetime.now()
                        )
                        db.session.add(recordatorio)
                        recordatorios_creados += 1

            db.session.commit()
            if recordatorios_creados > 0:
                flash(f"{recordatorios_creados} recordatorios enviados a los inscritos", "success")
            else:
                flash("No hay nuevos recordatorios para enviar", "info")
        except Exception as e:
            db.session.rollback()
            flash(f"Error al enviar recordatorios: {str(e)}", "error")
            
        return redirect(url_for("listar_eventos"))