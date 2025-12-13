from flask import render_template, redirect, url_for, flash, request, session
from database import db
from models import Usuario, Sorteo, Vehiculo
from datetime import datetime
import random
from functools import wraps
import mysql.connector  # Añade esta importación

# Decorador DEFINITIVO - Verifica el rol REAL en la base de datos
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 1. Verificar si hay sesión
            if 'user_id' not in session:
                flash('Por favor inicie sesión para acceder a esta página.', 'error')
                return redirect(url_for('login'))
            
            # 2. Obtener usuario REAL de la base de datos
            usuario = Usuario.query.get(session['user_id'])
            if not usuario:
                flash('Usuario no encontrado.', 'error')
                session.clear()
                return redirect(url_for('login'))
            
            # 3. ACTUALIZAR la sesión con datos REALES de la BD
            session['rol'] = usuario.ROL
            session['nombre'] = f"{usuario.NOMBRE} {usuario.APELLIDO}"
            
            # 4. Si no se especifica rol, permitir acceso
            if role is None:
                return f(*args, **kwargs)
            
            # 5. Verificar si el rol REAL coincide con el requerido
            if usuario.ROL != role:
                flash(f'Acceso denegado. Se requiere rol {role}. Su rol es {usuario.ROL}.', 'error')
                
                # Redirigir según el rol REAL
                if usuario.ROL == 'ADMINISTRADOR':
                    return redirect(url_for('listar_sorteos'))
                else:
                    return redirect(url_for('login'))
            
            # 6. Acceso permitido
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# CONFIGURACIÓN DE CUPOS POR TIPO DE VEHÍCULO
CUPOS_PARQUEADEROS = {
    'CARRO': 70,
    'MOTO': 120, 
    'BICICLETA': 100
}

def init_sorteo_routes(app):
    # -----------------------------
    # 📋 LISTAR SORTEOS
    # -----------------------------
    @app.route('/sorteos')
    @login_required('ADMINISTRADOR')
    def listar_sorteos():
        # Obtener todos los sorteos con información del usuario
        sorteos = Sorteo.query.join(Usuario).order_by(Sorteo.FECHA.desc()).all()
        
        # Obtener estadísticas de vehículos aprobados
        estadisticas = {}
        for tipo in ['CARRO', 'MOTO', 'BICICLETA']:
            total_aprobados = Vehiculo.query.filter_by(
                TIPO=tipo, 
                ESTADO='APROBADO'
            ).count()
            
            estadisticas[tipo] = {
                'aprobados': total_aprobados,
                'cupos': CUPOS_PARQUEADEROS[tipo],
                'disponible': CUPOS_PARQUEADEROS[tipo] - total_aprobados if total_aprobados < CUPOS_PARQUEADEROS[tipo] else 0,
                'suficientes': total_aprobados >= CUPOS_PARQUEADEROS[tipo]
            }
        
        return render_template('listar_sorteos.html', 
                             sorteos=sorteos, 
                             cupos=CUPOS_PARQUEADEROS,
                             estadisticas=estadisticas)

    # -----------------------------
    # 🎯 CREAR SORTEO (MEJORADO - Solo residentes APROBADOS)
    # -----------------------------
    @app.route('/crear_sorteo/<tipo>')
    @login_required('ADMINISTRADOR')
    def crear_sorteo(tipo):
        # Verificar que el tipo sea válido
        if tipo not in ['CARRO', 'MOTO', 'BICICLETA']:
            flash('Tipo de vehículo no válido.', 'error')
            return redirect(url_for('listar_sorteos'))
        
        # Obtener cupos según tipo de vehículo
        cupos = CUPOS_PARQUEADEROS.get(tipo, 0)
        
        if cupos == 0:
            flash(f"Tipo de vehículo {tipo} no configurado", "error")
            return redirect(url_for("listar_sorteos"))

        # SOLO residentes ACTIVOS con vehículos APROBADOS del tipo correspondiente
        usuarios_aprobados = db.session.query(Usuario).join(
            Vehiculo, 
            Usuario.ID_USUARIO == Vehiculo.ID_USUARIO
        ).filter(
            Usuario.ROL == "RESIDENTE",
            Usuario.ESTADO == "ACTIVO",  # Solo residentes activos
            Vehiculo.TIPO == tipo,
            Vehiculo.ESTADO == "APROBADO"  # Solo vehículos APROBADOS
        ).all()

        if not usuarios_aprobados:
            flash(f'No hay vehículos APROBADOS de tipo {tipo} para realizar el sorteo.', 'warning')
            return redirect(url_for('listar_sorteos'))
        
        # Verificar que hay suficientes participantes
        if len(usuarios_aprobados) < cupos:
            flash(f"⚠️ Solo hay {len(usuarios_aprobados)} vehículos APROBADOS para {cupos} cupos de {tipo}. Todos obtendrán parqueadero.", "warning")

        # Realizar sorteo (mezclar aleatoriamente)
        random.shuffle(usuarios_aprobados)
        
        # Determinar ganadores (todos si hay menos participantes que cupos)
        if len(usuarios_aprobados) <= cupos:
            ganadores = usuarios_aprobados
            en_espera = []
        else:
            ganadores = usuarios_aprobados[:cupos]
            en_espera = usuarios_aprobados[cupos:]

        # Eliminar sorteos previos del mismo tipo (opcional, descomentar si quieres)
        # Sorteo.query.filter_by(TIPO=tipo).delete()
        # db.session.commit()

        # Registrar ganadores
        for usuario in ganadores:
            # Verificar si ya existe un sorteo ganador para este usuario y tipo
            sorteo_existente = Sorteo.query.filter_by(
                ID_USUARIO=usuario.ID_USUARIO,
                TIPO=tipo,
                RESULTADO="GANADOR"
            ).first()
            
            if not sorteo_existente:
                db.session.add(Sorteo(
                    FECHA=datetime.now(), 
                    TIPO=tipo, 
                    ID_USUARIO=usuario.ID_USUARIO, 
                    RESULTADO="GANADOR"
                ))

        # Registrar lista de espera (solo si hay más participantes que cupos)
        if en_espera:
            for usuario in en_espera:
                # Verificar si ya existe en lista de espera
                sorteo_existente = Sorteo.query.filter_by(
                    ID_USUARIO=usuario.ID_USUARIO,
                    TIPO=tipo,
                    RESULTADO="ESPERA"
                ).first()
                
                if not sorteo_existente:
                    db.session.add(Sorteo(
                        FECHA=datetime.now(), 
                        TIPO=tipo, 
                        ID_USUARIO=usuario.ID_USUARIO, 
                        RESULTADO="ESPERA"
                    ))

        try:
            db.session.commit()
            
            if len(usuarios_aprobados) <= cupos:
                flash(f'✅ Todos los {len(usuarios_aprobados)} vehículos APROBADOS de tipo {tipo} obtuvieron parqueadero.', 'success')
            else:
                flash(f'✅ Sorteo realizado: {len(ganadores)} ganadores y {len(en_espera)} en lista de espera para {tipo}.', 'success')
                
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al realizar el sorteo: {str(e)}', 'error')
        
        return redirect(url_for('listar_sorteos'))

    # -----------------------------
    # 📊 ESTADÍSTICAS DE SORTEOS - VERSIÓN MEJORADA CON DATOS REALES
    # -----------------------------
    @app.route('/estadisticas_sorteos')
    @login_required('ADMINISTRADOR')
    def estadisticas_sorteos():
        try:
            # Conectar a la base de datos (Ajusta las credenciales según tu configuración)
            conn = mysql.connector.connect(
                host='127.0.0.1',
                user='root',  # Usuario de MySQL (ajusta según tu configuración)
                password='',  # Contraseña de MySQL (dejar vacío si no tiene)
                database='sistema_residencial'
            )
            cursor = conn.cursor(dictionary=True)
            
            # 1. Obtener estadísticas de sorteos por tipo y resultado
            cursor.execute("""
                SELECT 
                    TIPO,
                    RESULTADO,
                    COUNT(*) as cantidad
                FROM sorteo 
                GROUP BY TIPO, RESULTADO
            """)
            sorteos_data = cursor.fetchall()
            
            # 2. Obtener vehículos aprobados por tipo
            cursor.execute("""
                SELECT 
                    TIPO,
                    COUNT(*) as cantidad
                FROM vehiculo 
                WHERE ESTADO = 'APROBADO'
                GROUP BY TIPO
            """)
            vehiculos_aprobados = cursor.fetchall()
            
            # 3. Obtener total de vehículos por tipo
            cursor.execute("""
                SELECT 
                    TIPO,
                    COUNT(*) as cantidad
                FROM vehiculo 
                GROUP BY TIPO
            """)
            total_vehiculos = cursor.fetchall()
            
            # 4. Obtener residentes activos
            cursor.execute("""
                SELECT COUNT(*) as cantidad 
                FROM usuario 
                WHERE ROL = 'RESIDENTE' AND ESTADO = 'ACTIVO'
            """)
            residentes_activos_result = cursor.fetchone()
            residentes_activos = residentes_activos_result['cantidad'] if residentes_activos_result else 0
            
            # 5. Obtener el último sorteo para fecha de actualización
            cursor.execute("SELECT MAX(FECHA) as ultima_fecha FROM sorteo")
            ultima_fecha_result = cursor.fetchone()
            ultima_fecha = ultima_fecha_result['ultima_fecha'] if ultima_fecha_result else None
            
            cursor.close()
            conn.close()
            
            # Procesar datos de sorteos
            estadisticas = {
                'CARRO': {'ganadores': 0, 'espera': 0, 'total': 0},
                'MOTO': {'ganadores': 0, 'espera': 0, 'total': 0},
                'BICICLETA': {'ganadores': 0, 'espera': 0, 'total': 0}
            }
            
            for fila in sorteos_data:
                tipo = fila['TIPO']
                resultado = fila['RESULTADO']
                cantidad = fila['cantidad']
                
                if tipo in estadisticas:
                    estadisticas[tipo]['total'] += cantidad
                    if resultado == 'GANADOR':
                        estadisticas[tipo]['ganadores'] += cantidad
                    else:
                        estadisticas[tipo]['espera'] += cantidad
            
            # Procesar vehículos aprobados
            vehiculos_aprob = {
                'CARRO': 0,
                'MOTO': 0,
                'BICICLETA': 0
            }
            
            for fila in vehiculos_aprobados:
                vehiculos_aprob[fila['TIPO']] = fila['cantidad']
            
            # Procesar total de vehículos
            vehiculos_total = {
                'CARRO': 0,
                'MOTO': 0,
                'BICICLETA': 0
            }
            
            for fila in total_vehiculos:
                vehiculos_total[fila['TIPO']] = fila['cantidad']
            
            # Calcular totales generales
            total_sorteos = sum(v['total'] for v in estadisticas.values())
            total_ganadores = sum(v['ganadores'] for v in estadisticas.values())
            total_espera = sum(v['espera'] for v in estadisticas.values())
            
            # Formatear fecha
            fecha_actualizacion = datetime.now().strftime('%d/%m/%Y %H:%M')
            if ultima_fecha:
                fecha_actualizacion = ultima_fecha.strftime('%d/%m/%Y %H:%M')
            
            return render_template('estadisticas_sorteos.html',
                estadisticas=estadisticas,
                vehiculos_aprobados=vehiculos_aprob,
                vehiculos_registrados=vehiculos_total,
                residentes_activos=residentes_activos,
                total_sorteos=total_sorteos,
                total_ganadores=total_ganadores,
                total_espera=total_espera,
                fecha_actualizacion=fecha_actualizacion,
                cupos=CUPOS_PARQUEADEROS
            )
            
        except Exception as e:
            print(f"Error en estadisticas_sorteos: {e}")
            
            # En caso de error, usar SQLAlchemy como fallback
            estadisticas = {}
            for tipo in ['CARRO', 'MOTO', 'BICICLETA']:
                # Vehículos APROBADOS
                total_aprobados = Vehiculo.query.filter_by(
                    TIPO=tipo, 
                    ESTADO='APROBADO'
                ).count()
                
                # Vehículos PENDIENTES (para información)
                total_pendientes = Vehiculo.query.filter_by(
                    TIPO=tipo, 
                    ESTADO='PENDIENTE'
                ).count()
                
                # Ganadores actuales
                total_ganadores = Sorteo.query.filter_by(
                    TIPO=tipo,
                    RESULTADO='GANADOR'
                ).count()
                
                # En espera
                total_espera = Sorteo.query.filter_by(
                    TIPO=tipo,
                    RESULTADO='ESPERA'
                ).count()
                
                estadisticas[tipo] = {
                    'aprobados': total_aprobados,
                    'pendientes': total_pendientes,
                    'ganadores': total_ganadores,
                    'espera': total_espera,
                    'total': total_ganadores + total_espera,
                    'cupos': CUPOS_PARQUEADEROS[tipo],
                    'disponible': CUPOS_PARQUEADEROS[tipo] - total_aprobados if total_aprobados < CUPOS_PARQUEADEROS[tipo] else 0,
                    'suficientes': total_aprobados >= CUPOS_PARQUEADEROS[tipo]
                }
            
            total_sorteos = sum(v['total'] for v in estadisticas.values())
            total_ganadores = sum(v['ganadores'] for v in estadisticas.values())
            total_espera = sum(v['espera'] for v in estadisticas.values())
            
            vehiculos_aprob = {tipo: estadisticas[tipo]['aprobados'] for tipo in ['CARRO', 'MOTO', 'BICICLETA']}
            vehiculos_total = {tipo: estadisticas[tipo]['aprobados'] + estadisticas[tipo]['pendientes'] for tipo in ['CARRO', 'MOTO', 'BICICLETA']}
            
            residentes_activos = Usuario.query.filter_by(ROL='RESIDENTE', ESTADO='ACTIVO').count()
            
            return render_template('estadisticas_sorteos.html',
                estadisticas=estadisticas,
                vehiculos_aprobados=vehiculos_aprob,
                vehiculos_registrados=vehiculos_total,
                residentes_activos=residentes_activos,
                total_sorteos=total_sorteos,
                total_ganadores=total_ganadores,
                total_espera=total_espera,
                fecha_actualizacion=datetime.now().strftime('%d/%m/%Y %H:%M'),
                cupos=CUPOS_PARQUEADEROS
            )

    # -----------------------------
    # 🅿️ ASIGNAR PARQUEADEROS
    # -----------------------------
    @app.route('/asignar_parqueaderos/<int:id_sorteo>')
    @login_required('ADMINISTRADOR')
    def asignar_parqueaderos(id_sorteo):
        # Obtener el sorteo
        sorteo = Sorteo.query.get_or_404(id_sorteo)
        
        # Obtener todos los ganadores de este tipo de sorteo
        ganadores = Sorteo.query.filter_by(
            TIPO=sorteo.TIPO,
            RESULTADO='GANADOR'
        ).join(Usuario).order_by(Sorteo.FECHA.desc()).all()
        
        # Generar números de parqueadero según el tipo
        if sorteo.TIPO == 'CARRO':
            parqueaderos = [f'C-{i:03d}' for i in range(1, 71)]
        elif sorteo.TIPO == 'MOTO':
            parqueaderos = [f'M-{i:03d}' for i in range(1, 121)]
        else:  # BICICLETA
            parqueaderos = [f'B-{i:03d}' for i in range(1, 101)]
        
        # Verificar que hay suficientes parqueaderos
        if len(ganadores) > len(parqueaderos):
            flash(f'⚠️ Hay más ganadores ({len(ganadores)}) que parqueaderos disponibles ({len(parqueaderos)})', 'warning')
        
        return render_template('asignar_parqueaderos.html', 
                             sorteo=sorteo, 
                             ganadores=ganadores,
                             parqueaderos=parqueaderos[:len(ganadores)])

    # -----------------------------
    # 🖨️ IMPRIMIR ASIGNACIÓN
    # -----------------------------
    @app.route('/imprimir_asignacion/<int:id_sorteo>')
    @login_required('ADMINISTRADOR')
    def imprimir_asignacion(id_sorteo):
        # Obtener el sorteo
        sorteo = Sorteo.query.get_or_404(id_sorteo)
        
        # Obtener todos los ganadores de este tipo de sorteo
        ganadores = Sorteo.query.filter_by(
            TIPO=sorteo.TIPO,
            RESULTADO='GANADOR'
        ).join(Usuario).order_by(Sorteo.FECHA.desc()).all()
        
        # Generar números de parqueadero según el tipo
        if sorteo.TIPO == 'CARRO':
            parqueaderos = [f'C-{i:03d}' for i in range(1, 71)]
        elif sorteo.TIPO == 'MOTO':
            parqueaderos = [f'M-{i:03d}' for i in range(1, 121)]
        else:  # BICICLETA
            parqueaderos = [f'B-{i:03d}' for i in range(1, 101)]
        
        # Crear asignaciones
        asignaciones = []
        for i, ganador in enumerate(ganadores[:len(parqueaderos)]):
            asignaciones.append({
                'parqueadero': parqueaderos[i],
                'residente': ganador.usuario,
                'vehiculo': Vehiculo.query.filter_by(
                    ID_USUARIO=ganador.ID_USUARIO,
                    TIPO=sorteo.TIPO,
                    ESTADO='APROBADO'
                ).first()
            })
        
        return render_template('imprimir_asignacion.html',
                            sorteo=sorteo,
                            asignaciones=asignaciones,
                            fecha=datetime.now().strftime('%d/%m/%Y %H:%M'))