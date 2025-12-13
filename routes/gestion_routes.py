# routes/gestion_routes.py
from flask import render_template, request, flash, session
from database import db
from models import GestionEspera, Evento
from datetime import datetime
from .utils import login_required

def init_gestion_routes(app):
    @app.route("/lista_de_gestion_espera", methods=["GET", "POST"])
    @login_required('ADMINISTRADOR')
    def lista_de_gestion_espera():
        if request.method == "POST":
            try:
                detalle = request.form["detalle"]
                nuevo = GestionEspera(DETALLE=detalle, SOLICITADO_POR=session.get("user_id"))
                db.session.add(nuevo)
                db.session.commit()
                flash("Solicitud añadida a lista de espera", "exito")
            except Exception as e:
                db.session.rollback()
                flash(f"Error: {str(e)}", "error")
        
        espera = GestionEspera.query.order_by(GestionEspera.FECHA_SOLICITUD.desc()).all()
        return render_template("lista_de_gestion_espera.html", 
                             espera=espera,
                             user_name=session.get('user_name'),
                             user_role=session.get('user_role'))

    @app.route("/agendamiento_de_evento", methods=["GET", "POST"])
    @login_required('RESIDENTE')
    def agendamiento_de_evento():
        if request.method == "POST":
            try:
                titulo = request.form["titulo"]
                descripcion = request.form["descripcion"]
                fecha = datetime.strptime(request.form["fecha"], "%Y-%m-%d %H:%M")
                nuevo = Evento(TITULO=titulo, DESCRIPCION=descripcion, FECHA=fecha,
                               CREADO_POR=session.get("user_id"))
                db.session.add(nuevo)
                db.session.commit()
                flash("Evento agendado correctamente", "exito")
            except Exception as e:
                db.session.rollback()
                flash(f"Error al agendar evento: {str(e)}", "error")
        
        eventos = Evento.query.order_by(Evento.FECHA.desc()).all()
        return render_template("agendamiento_de_evento.html", 
                             eventos=eventos,
                             user_name=session.get('user_name'),
                             user_role=session.get('user_role'))