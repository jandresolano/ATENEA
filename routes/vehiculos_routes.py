# routes/vehiculos_routes.py - Versión corregida
from flask import render_template, request, redirect, url_for, flash, session, send_file, jsonify  # <-- AGREGAR jsonify
from database import db
from datetime import datetime
import os
import logging
from werkzeug.utils import secure_filename


# --- Import seguro del middleware ---
try:
    from middleware import login_required
except ImportError:
    from functools import wraps
    def login_required(role=None):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if 'user_id' not in session:
                    flash('Debes iniciar sesión para acceder a esta página', 'error')
                    return redirect(url_for('login'))
                if role and session.get('user_role') != role:
                    flash('No tienes permisos para acceder a esta página', 'error')
                    return redirect(url_for("inicio"))
                return f(*args, **kwargs)
            return decorated_function
        return decorator

def init_vehiculos_routes(app):
    
    # Configuración para subida de archivos
    UPLOAD_FOLDER = 'static/uploads/vehiculos'
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
    MAX_FILE_SIZE = 16 * 1024 * 1024
    
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Función auxiliar para manejar nombres de columnas
    def set_vehiculo_documentos(vehiculo, archivos_subidos):
        """Asigna los documentos al vehículo manejando diferentes nombres de columnas"""
        try:
            # Usar solo DOC_TARJETA_PROPIEDAD (eliminar referencia a DOC_TARJETA_PROPIEIDAD)
            if hasattr(vehiculo, 'DOC_TARJETA_PROPIEDAD'):
                vehiculo.DOC_TARJETA_PROPIEDAD = archivos_subidos.get('tarjeta_propiedad')
            
            # Estas columnas deberían estar bien
            if hasattr(vehiculo, 'DOC_SOAT'):
                vehiculo.DOC_SOAT = archivos_subidos.get('soat')
            if hasattr(vehiculo, 'DOC_IDENTIDAD'):
                vehiculo.DOC_IDENTIDAD = archivos_subidos.get('identidad')
            if hasattr(vehiculo, 'ESTADO'):
                vehiculo.ESTADO = 'PENDIENTE'
            if hasattr(vehiculo, 'FECHA_REGISTRO'):
                vehiculo.FECHA_REGISTRO = datetime.now()
                
        except Exception as e:
            print(f"Error al asignar documentos: {e}")
    
    def get_vehiculo_tarjeta_propiedad(vehiculo):
        """Obtiene el nombre del archivo de tarjeta de propiedad"""
        if hasattr(vehiculo, 'DOC_TARJETA_PROPIEDAD') and getattr(vehiculo, 'DOC_TARJETA_PROPIEDAD'):
            return getattr(vehiculo, 'DOC_TARJETA_PROPIEDAD')
        return None
    
    # -----------------------------
    # 📋 LISTAR VEHÍCULOS - VERSIÓN MEJORADA
    # -----------------------------
    @app.route('/vehiculos')
    @login_required()
    def listar_vehiculos():
        from models import Vehiculo, Usuario
        
        user_id = session.get('user_id')
        rol = session.get('user_role')

        if rol == 'ADMINISTRADOR':
            vehiculos = db.session.query(Vehiculo, Usuario).join(Usuario, Vehiculo.ID_USUARIO == Usuario.ID_USUARIO).all()
            
            # Estadísticas para administradores
            total_vehiculos = Vehiculo.query.count()
            vehiculos_pendientes = Vehiculo.query.filter_by(ESTADO='PENDIENTE').count()
            vehiculos_aprobados = Vehiculo.query.filter_by(ESTADO='APROBADO').count()
            vehiculos_rechazados = Vehiculo.query.filter_by(ESTADO='RECHAZADO').count()
            
            return render_template('vehiculos.html', 
                                vehiculos=vehiculos, 
                                user_role=rol,
                                total_vehiculos=total_vehiculos,
                                vehiculos_pendientes=vehiculos_pendientes,
                                vehiculos_aprobados=vehiculos_aprobados,
                                vehiculos_rechazados=vehiculos_rechazados)
        else:
            vehiculos = Vehiculo.query.filter_by(ID_USUARIO=user_id).all()
            return render_template('vehiculos.html', 
                                vehiculos=vehiculos, 
                                user_role=rol,
                                total_vehiculos=len(vehiculos),
                                vehiculos_pendientes=0,
                                vehiculos_aprobados=0,
                                vehiculos_rechazados=0)
    # -----------------------------
    # 🚗 CREAR VEHÍCULO
    # -----------------------------
    @app.route('/vehiculos/crear', methods=['GET', 'POST'])
    @login_required('RESIDENTE')
    def crear_vehiculo():
        from models import Vehiculo

        if request.method == 'POST':
            archivos_subidos = {}
            try:
                placa = request.form.get('placa', '').strip().upper()
                tipo = request.form.get('tipo', '')
                
                if not placa or not tipo:
                    flash('La placa y el tipo de vehículo son obligatorios', 'error')
                    return render_template('crear_vehiculo.html')
                
                # Verificar si ya existe la placa
                vehiculo_existente = Vehiculo.query.filter_by(PLACA=placa).first()
                if vehiculo_existente:
                    flash('Ya existe un vehículo con esta placa', 'error')
                    return render_template('crear_vehiculo.html')
                
                # Procesar archivos
                documentos_requeridos = {
                    'soat': 'SOAT',
                    'identidad': 'Documento de Identidad', 
                    'tarjeta_propiedad': 'Tarjeta de Propiedad'
                }
                
                for doc_key, doc_name in documentos_requeridos.items():
                    file = request.files.get(doc_key)
                    if not file or not file.filename:
                        flash(f'El {doc_name} es requerido', 'error')
                        return render_template('crear_vehiculo.html')
                    
                    if not allowed_file(file.filename):
                        flash(f'El {doc_name} debe ser PDF, PNG, JPG o JPEG', 'error')
                        return render_template('crear_vehiculo.html')
                    
                    file.seek(0, os.SEEK_END)
                    if file.tell() > MAX_FILE_SIZE:
                        flash(f'El {doc_name} es demasiado grande. Máximo 16MB', 'error')
                        return render_template('crear_vehiculo.html')
                    file.seek(0)
                    
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    file_extension = file.filename.rsplit('.', 1)[1].lower()
                    filename = f"{placa}_{doc_key}_{timestamp}.{file_extension}"
                    filename = secure_filename(filename)
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    
                    try:
                        file.save(filepath)
                        archivos_subidos[doc_key] = filename
                    except Exception as e:
                        flash(f'Error al guardar el {doc_name}: {str(e)}', 'error')
                        return render_template('crear_vehiculo.html')
                
                # Crear vehículo
                nuevo_vehiculo = Vehiculo(
                    PLACA=placa,
                    TIPO=tipo,
                    ID_USUARIO=session.get('user_id')
                )
                
                # Asignar documentos usando la función auxiliar
                set_vehiculo_documentos(nuevo_vehiculo, archivos_subidos)
                
                db.session.add(nuevo_vehiculo)
                db.session.commit()
                
                flash('✅ Vehículo registrado exitosamente. Pendiente de aprobación por administración.', 'success')
                return redirect(url_for('listar_vehiculos'))
            
            except Exception as e:
                db.session.rollback()
                # Eliminar archivos subidos en caso de error
                for filename in archivos_subidos.values():
                    try:
                        filepath = os.path.join(UPLOAD_FOLDER, filename)
                        if os.path.exists(filepath):
                            os.remove(filepath)
                    except:
                        pass
                flash(f'❌ Error al registrar el vehículo: {str(e)}', 'error')
                return render_template('crear_vehiculo.html')
        
        return render_template('crear_vehiculo.html')

    # -----------------------------
    # ✏️ EDITAR VEHÍCULO
    # -----------------------------
    @app.route('/vehiculos/editar/<int:id>', methods=['GET', 'POST'])
    @login_required()
    def editar_vehiculo(id):
        from models import Vehiculo
        
        vehiculo = Vehiculo.query.get_or_404(id)
        rol = session.get('user_role')
        user_id = session.get('user_id')
        
        # Validar permisos
        if rol != 'ADMINISTRADOR' and vehiculo.ID_USUARIO != user_id:
            flash('No tienes permisos para editar este vehículo', 'error')
            return redirect(url_for('listar_vehiculos'))
        
        # Solo permitir edición si está pendiente o es administrador
        if rol != 'ADMINISTRADOR' and getattr(vehiculo, 'ESTADO', 'PENDIENTE') != 'PENDIENTE':
            flash('No puedes editar un vehículo que ya fue revisado', 'error')
            return redirect(url_for('listar_vehiculos'))
        
        if request.method == 'POST':
            archivos_subidos = {}
            try:
                placa = request.form.get('placa', '').strip().upper()
                tipo = request.form.get('tipo', '')
                
                if not placa or not tipo:
                    flash('La placa y el tipo de vehículo son obligatorios', 'error')
                    return render_template('editar_vehiculo.html', vehiculo=vehiculo)
                
                # Verificar duplicados de placa
                existente = Vehiculo.query.filter(
                    Vehiculo.PLACA == placa,
                    Vehiculo.ID_VEHICULO != id
                ).first()
                if existente:
                    flash('Ya existe otro vehículo con esa placa', 'error')
                    return render_template('editar_vehiculo.html', vehiculo=vehiculo)
                
                # Procesar archivos subidos (opcionales en edición)
                for doc_key in ['soat', 'identidad', 'tarjeta_propiedad']:
                    file = request.files.get(doc_key)
                    if file and file.filename:
                        if not allowed_file(file.filename):
                            flash(f'El documento debe ser PDF, PNG, JPG o JPEG', 'error')
                            return render_template('editar_vehiculo.html', vehiculo=vehiculo)
                        
                        file.seek(0, os.SEEK_END)
                        if file.tell() > MAX_FILE_SIZE:
                            flash(f'El documento es demasiado grande. Máximo 16MB', 'error')
                            return render_template('editar_vehiculo.html', vehiculo=vehiculo)
                        file.seek(0)
                        
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        file_extension = file.filename.rsplit('.', 1)[1].lower()
                        filename = f"{placa}_{doc_key}_{timestamp}.{file_extension}"
                        filename = secure_filename(filename)
                        filepath = os.path.join(UPLOAD_FOLDER, filename)
                        
                        try:
                            file.save(filepath)
                            archivos_subidos[doc_key] = filename
                        except Exception as e:
                            flash(f'Error al guardar el documento: {str(e)}', 'error')
                            return render_template('editar_vehiculo.html', vehiculo=vehiculo)
                
                # Actualizar datos básicos
                vehiculo.PLACA = placa
                vehiculo.TIPO = tipo
                
                # Actualizar documentos si se subieron nuevos
                if archivos_subidos:
                    set_vehiculo_documentos(vehiculo, archivos_subidos)
                    # Si se actualizaron documentos, cambiar estado a pendiente
                    if rol != 'ADMINISTRADOR' and hasattr(vehiculo, 'ESTADO'):
                        vehiculo.ESTADO = 'PENDIENTE'
                        flash('✅ Vehículo actualizado. Estado cambiado a PENDIENTE para revisión de nuevos documentos.', 'success')
                    else:
                        flash('✅ Vehículo actualizado correctamente', 'success')
                else:
                    flash('✅ Vehículo actualizado correctamente', 'success')
                
                db.session.commit()
                return redirect(url_for('listar_vehiculos'))
            
            except Exception as e:
                db.session.rollback()
                # Eliminar archivos subidos en caso de error
                for filename in archivos_subidos.values():
                    try:
                        filepath = os.path.join(UPLOAD_FOLDER, filename)
                        if os.path.exists(filepath):
                            os.remove(filepath)
                    except:
                        pass
                flash(f'❌ Error al actualizar vehículo: {str(e)}', 'error')
                return render_template('editar_vehiculo.html', vehiculo=vehiculo)
        
        return render_template('editar_vehiculo.html', vehiculo=vehiculo)

    # -----------------------------
    # 📄 DESCARGAR DOCUMENTO - VERSIÓN DEFINITIVA
    # -----------------------------
    @app.route('/vehiculos/descargar/<filename>')
    @login_required()
    def descargar_documento(filename):
        from models import Vehiculo
        
        try:
            print(f"🔍 Buscando documento: {filename}")
            
            # Buscar en TODOS los campos de documentos
            vehiculo = Vehiculo.query.filter(
                (Vehiculo.DOC_SOAT == filename) | 
                (Vehiculo.DOC_IDENTIDAD == filename) |
                (Vehiculo.DOC_TARJETA_PROPIEDAD == filename)
            ).first()
            
            if not vehiculo:
                print(f"❌ Documento NO encontrado en BD: {filename}")
                flash('Documento no encontrado en la base de datos', 'error')
                return redirect(url_for('listar_vehiculos'))
            
            print(f"✅ Documento encontrado en vehículo: {vehiculo.PLACA}")
            
            rol = session.get('user_role')
            user_id = session.get('user_id')
            
            # Validar permisos
            if rol != 'ADMINISTRADOR' and vehiculo.ID_USUARIO != user_id:
                flash('No tienes permisos para acceder a este documento', 'error')
                return redirect(url_for('listar_vehiculos'))
            
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            print(f"📁 Ruta del archivo: {filepath}")
            print(f"📁 Ruta absoluta: {os.path.abspath(filepath)}")
            
            if not os.path.exists(filepath):
                print(f"❌ Archivo NO existe en servidor: {filepath}")
                
                # Verificar si hay archivos con nombres similares
                archivos_similares = []
                if os.path.exists(UPLOAD_FOLDER):
                    for archivo in os.listdir(UPLOAD_FOLDER):
                        if filename.lower() in archivo.lower():
                            archivos_similares.append(archivo)
                
                if archivos_similares:
                    print(f"📂 Archivos similares encontrados: {archivos_similares}")
                
                flash('Archivo no encontrado en el servidor', 'error')
                return redirect(url_for('listar_vehiculos'))
            
            print(f"✅ Archivo existe, enviando: {filename}")
            return send_file(filepath, as_attachment=True)
            
        except Exception as e:
            print(f"💥 Error grave al descargar documento: {str(e)}")
            flash(f'Error al descargar documento: {str(e)}', 'error')
            return redirect(url_for('listar_vehiculos'))
    # -----------------------------
    # ✅ APROBAR VEHÍCULO (Admin)
    # -----------------------------
    @app.route('/vehiculos/aprobar/<int:id>')
    @login_required('ADMINISTRADOR')
    def aprobar_vehiculo(id):
        from models import Vehiculo
        
        vehiculo = Vehiculo.query.get_or_404(id)
        
        try:
            if hasattr(vehiculo, 'ESTADO'):
                vehiculo.ESTADO = 'APROBADO'
                db.session.commit()
                flash('✅ Vehículo aprobado exitosamente', 'success')
            else:
                flash('❌ La columna ESTADO no existe en la base de datos', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al aprobar vehículo: {str(e)}', 'error')
        
        return redirect(url_for('listar_vehiculos'))

    # -----------------------------
    # ❌ RECHAZAR VEHÍCULO (Admin)
    # -----------------------------
    @app.route('/vehiculos/rechazar/<int:id>')
    @login_required('ADMINISTRADOR')
    def rechazar_vehiculo(id):
        from models import Vehiculo
        
        vehiculo = Vehiculo.query.get_or_404(id)
        
        try:
            if hasattr(vehiculo, 'ESTADO'):
                vehiculo.ESTADO = 'RECHAZADO'
                db.session.commit()
                flash('✅ Vehículo rechazado', 'success')
            else:
                flash('❌ La columna ESTADO no existe en la base de datos', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al rechazar vehículo: {str(e)}', 'error')
        
        return redirect(url_for('listar_vehiculos'))

    # -----------------------------
    # 🗑️ ELIMINAR VEHÍCULO
    # -----------------------------
    @app.route('/vehiculos/eliminar/<int:id>')
    @login_required()
    def eliminar_vehiculo(id):
        from models import Vehiculo
        
        vehiculo = Vehiculo.query.get_or_404(id)
        rol = session.get('user_role')
        user_id = session.get('user_id')
        
        # Validar permisos
        if rol != 'ADMINISTRADOR' and vehiculo.ID_USUARIO != user_id:
            flash('No tienes permisos para eliminar este vehículo', 'error')
            return redirect(url_for('listar_vehiculos'))
        
        try:
            # Eliminar archivos asociados
            documentos = []
            if hasattr(vehiculo, 'DOC_SOAT') and getattr(vehiculo, 'DOC_SOAT'):
                documentos.append(getattr(vehiculo, 'DOC_SOAT'))
            if hasattr(vehiculo, 'DOC_IDENTIDAD') and getattr(vehiculo, 'DOC_IDENTIDAD'):
                documentos.append(getattr(vehiculo, 'DOC_IDENTIDAD'))
            
            tarjeta_propiedad = get_vehiculo_tarjeta_propiedad(vehiculo)
            if tarjeta_propiedad:
                documentos.append(tarjeta_propiedad)
            
            for documento in documentos:
                if documento:
                    filepath = os.path.join(UPLOAD_FOLDER, documento)
                    if os.path.exists(filepath):
                        os.remove(filepath)
            
            db.session.delete(vehiculo)
            db.session.commit()
            flash('✅ Vehículo eliminado exitosamente', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al eliminar vehículo: {str(e)}', 'error')
        
        return redirect(url_for('listar_vehiculos'))
    # -----------------------------
    # 🔍 DEPURAR DOCUMENTOS (temporal)
    # -----------------------------
    @app.route('/vehiculos/debug_documentos')
    @login_required('ADMINISTRADOR')
    def debug_documentos():
        from models import Vehiculo
        
        vehiculos = Vehiculo.query.all()
        documentos_info = []
        
        for vehiculo in vehiculos:
            documentos_info.append({
                'id': vehiculo.ID_VEHICULO,
                'placa': vehiculo.PLACA,
                'soat': vehiculo.DOC_SOAT,
                'identidad': vehiculo.DOC_IDENTIDAD,
                'propiedad': vehiculo.DOC_TARJETA_PROPIEDAD,
                'estado': vehiculo.ESTADO
            })
        
        return jsonify(documentos_info)
    
    # -----------------------------
    # 📁 LISTAR ARCHIVOS EN DIRECTORIO (temporal)
    # -----------------------------
    @app.route('/vehiculos/debug_archivos')
    @login_required('ADMINISTRADOR')
    def debug_archivos():
        archivos = []
        try:
            if os.path.exists(UPLOAD_FOLDER):
                for filename in os.listdir(UPLOAD_FOLDER):
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    archivos.append({
                        'nombre': filename,
                        'existe': True,
                        'tamaño': os.path.getsize(filepath) if os.path.isfile(filepath) else 0
                    })
            else:
                archivos.append({'error': f'La carpeta {UPLOAD_FOLDER} no existe'})
        except Exception as e:
            archivos.append({'error': str(e)})
        
        return jsonify({
            'ruta_absoluta': os.path.abspath(UPLOAD_FOLDER),
            'archivos': archivos
        })