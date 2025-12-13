# routes/seguridad_routes.py
from flask import render_template, request, flash, session
from database import db
from models import Incidente
from .utils import login_required

def init_seguridad_routes(app):
    @app.route("/seguridad_monitoreo", methods=["GET", "POST"])
    @login_required('PORTERO')
    def seguridad_monitoreo():
        if request.method == "POST":
            try:
                detalle = request.form["detalle"]
                nuevo = Incidente(DETALLE=detalle, REPORTADO_POR=session.get("user_id"))
                db.session.add(nuevo)
                db.session.commit()
                flash("Incidente registrado", "exito")
            except Exception as e:
                db.session.rollback()
                flash(f"Error: {str(e)}", "error")
        
        incidentes = Incidente.query.order_by(Incidente.FECHA.desc()).all()
        return render_template("seguridad_monitoreo.html", 
                             incidentes=incidentes,
                             user_name=session.get('user_name'),
                             user_role=session.get('user_role'))