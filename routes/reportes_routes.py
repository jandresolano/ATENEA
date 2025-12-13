# routes/reportes_routes.py
from flask import render_template, request, flash, session
from database import db
from models import Reporte
from .utils import login_required

def init_reportes_routes(app):
    @app.route("/panel_de_reportes", methods=["GET", "POST"])
    @login_required('ADMINISTRADOR')
    def panel_de_reportes():
        if request.method == "POST":
            try:
                titulo = request.form["titulo"]
                detalle = request.form["detalle"]
                nuevo = Reporte(TITULO=titulo, DETALLE=detalle, CREADO_POR=session.get("user_id"))
                db.session.add(nuevo)
                db.session.commit()
                flash("Reporte creado exitosamente", "exito")
            except Exception as e:
                db.session.rollback()
                flash(f"Error al crear reporte: {str(e)}", "error")
        
        reportes = Reporte.query.order_by(Reporte.FECHA_REPORTE.desc()).all()
        return render_template("panel_de_reportes.html", 
                             reportes=reportes,
                             user_name=session.get('user_name'),
                             user_role=session.get('user_role'))