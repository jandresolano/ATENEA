# routes/parqueadero_routes.py
from flask import render_template, request, flash, session
from database import db
from models import PrestamoParqueadero
from datetime import datetime
from .utils import login_required

def init_parqueadero_routes(app):
    @app.route("/prestamo_temporal_parqueadero", methods=["GET", "POST"])
    @login_required('RESIDENTE')
    def prestamo_temporal_parqueadero():
        if request.method == "POST":
            try:
                vehiculo = request.form["vehiculo"]
                inicio = datetime.strptime(request.form["inicio"], "%Y-%m-%d %H:%M")
                fin = datetime.strptime(request.form["fin"], "%Y-%m-%d %H:%M")
                nuevo = PrestamoParqueadero(VEHICULO=vehiculo, INICIO=inicio, FIN=fin,
                                            RESIDENTE_ID=session.get("user_id"))
                db.session.add(nuevo)
                db.session.commit()
                flash("Préstamo de parqueadero solicitado", "exito")
            except Exception as e:
                db.session.rollback()
                flash(f"Error: {str(e)}", "error")
        
        prestamos = PrestamoParqueadero.query.order_by(PrestamoParqueadero.INICIO.desc()).all()
        return render_template("prestamo_temporal_parqueadero.html", 
                             prestamos=prestamos,
                             user_name=session.get('user_name'),
                             user_role=session.get('user_role'))

    @app.route("/mapa_interactivo")
    @login_required()
    def mapa_interactivo():
        return render_template("mapa_interactivo.html",
                             user_name=session.get('user_name'),
                             user_role=session.get('user_role'))