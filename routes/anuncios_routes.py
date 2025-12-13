# routes/anuncios_routes.py
from flask import render_template, request, flash, session
from database import db
from models import Anuncio
from .utils import login_required

def init_anuncios_routes(app):
    @app.route("/anuncios_masivos", methods=["GET", "POST"])
    @login_required('ADMINISTRADOR')
    def anuncios_masivos():
        if request.method == "POST":
            try:
                titulo = request.form["titulo"]
                mensaje = request.form["mensaje"]
                nuevo = Anuncio(TITULO=titulo, MENSAJE=mensaje, PUBLICADO_POR=session.get("user_id"))
                db.session.add(nuevo)
                db.session.commit()
                flash("Anuncio publicado", "exito")
            except Exception as e:
                db.session.rollback()
                flash(f"Error: {str(e)}", "error")
        
        anuncios = Anuncio.query.order_by(Anuncio.FECHA.desc()).all()
        return render_template("anuncios_masivos.html", 
                             anuncios=anuncios,
                             user_name=session.get('user_name'),
                             user_role=session.get('user_role'))