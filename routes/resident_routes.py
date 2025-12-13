# routes/resident_routes.py
import sys
import os
from flask import render_template, session, flash, redirect, url_for
from database import db
from models import Reserva, InscripcionEvento, RecordatorioEvento, Vehiculo
from datetime import datetime
from .utils import login_required

# Asegurar path correcto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def init_resident_routes(app):
    @app.route("/panel_residente")
    @login_required('RESIDENTE')
    def panel_residente():
        try:
            user_id = session.get('user_id')

            # Obtener eventos próximos (solo eventos ACTIVOS y futuros)
            eventos_proximos = Reserva.query.filter(
                Reserva.ESTADO == "ACTIVO",
                Reserva.FECHA_HORA >= datetime.now()
            ).order_by(Reserva.FECHA_HORA.asc()).limit(3).all()

            # Obtener inscripciones del usuario actual
            inscripciones = InscripcionEvento.query.filter_by(
                ID_USUARIO=user_id
            ).all()

            # Contar eventos inscritos
            eventos_inscritos = len(inscripciones)

            # Obtener IDs de eventos inscritos
            eventos_inscritos_ids = [i.ID_RESERVA for i in inscripciones]

            # Contar vehículos del residente
            vehiculos_count = Vehiculo.query.filter_by(ID_USUARIO=user_id).count()

            # (Opcional) Si más adelante usas recordatorios:
            # recordatorios = RecordatorioEvento.query.filter_by(ID_USUARIO=user_id).all()

            # Valores adicionales del panel
            eventos_pendientes = 0
            visitas_registradas = 0

            # Renderizar el panel con todos los datos
            return render_template(
                "panel_residente.html",
                user_name=session.get('user_name'),
                user_role=session.get('user_role'),
                eventos_proximos=eventos_proximos,
                eventos_inscritos=eventos_inscritos,
                eventos_pendientes=eventos_pendientes,
                visitas_registradas=visitas_registradas,
                eventos_inscritos_ids=eventos_inscritos_ids,
                vehiculos_count=vehiculos_count
            )

        except Exception as e:
            flash(f"Error al cargar el panel: {str(e)}", "error")
            return redirect(url_for("inicio"))
