# routes/actividades_routes.py
from flask import render_template, request, flash, session
from database import db
from models import Actividad
from .utils import login_required

def init_actividades_routes(app):
    @app.route("/historial_actividades", methods=["GET", "POST"])
    @login_required()
    def historial_actividades():
        if request.method == "POST":
            try:
                descripcion = request.form["descripcion"]
                nueva = Actividad(DESCRIPCION=descripcion, USUARIO_ID=session.get("user_id"))
                db.session.add(nueva)
                db.session.commit()
                flash("Actividad registrada", "exito")
            except Exception as e:
                db.session.rollback()
                flash(f"Error: {str(e)}", "error")
        
        actividades = Actividad.query.filter_by(USUARIO_ID=session.get("user_id")).all()
        return render_template("historial_actividades.html", 
                             actividades=actividades,
                             user_name=session.get('user_name'),
                             user_role=session.get('user_role'))