# routes/recibos_routes.py
from flask import render_template, request, flash, session
from database import db
from models import Recibo
from .utils import login_required

def init_recibos_routes(app):
    @app.route("/recibos_digitales", methods=["GET", "POST"])
    @login_required('RESIDENTE')
    def recibos_digitales():
        if request.method == "POST":
            try:
                monto = float(request.form["monto"])
                nuevo = Recibo(MONTO=monto, RESIDENTE_ID=session.get("user_id"))
                db.session.add(nuevo)
                db.session.commit()
                flash("Recibo generado", "exito")
            except Exception as e:
                db.session.rollback()
                flash(f"Error: {str(e)}", "error")
        
        recibos = Recibo.query.filter_by(RESIDENTE_ID=session.get("user_id")).all()
        return render_template("recibos_digitales.html", 
                             recibos=recibos,
                             user_name=session.get('user_name'),
                             user_role=session.get('user_role'))