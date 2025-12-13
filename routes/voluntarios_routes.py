# routes/voluntarios_routes.py
from flask import render_template, request, flash, session
from database import db
from models import Voluntario
from .utils import login_required

def init_voluntarios_routes(app):
    @app.route("/gestion_voluntarios", methods=["GET", "POST"])
    @login_required('ADMINISTRADOR')
    def gestion_voluntarios():
        if request.method == "POST":
            try:
                nombre = request.form["nombre"]
                actividad = request.form["actividad"]
                disponibilidad = request.form["disponibilidad"]
                contacto = request.form["contacto"]
                nuevo = Voluntario(NOMBRE=nombre, ACTIVIDAD=actividad,
                                   DISPONIBILIDAD=disponibilidad, CONTACTO=contacto)
                db.session.add(nuevo)
                db.session.commit()
                flash("Voluntario registrado", "exito")
            except Exception as e:
                db.session.rollback()
                flash(f"Error: {str(e)}", "error")
        
        voluntarios = Voluntario.query.all()
        return render_template("gestion_voluntarios.html", 
                             voluntarios=voluntarios,
                             user_name=session.get('user_name'),
                             user_role=session.get('user_role'))