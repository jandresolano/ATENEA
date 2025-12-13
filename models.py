from database import db
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = 'USUARIO'
    
    ID_USUARIO = db.Column(db.Integer, primary_key=True, autoincrement=True)
    NOMBRE = db.Column(db.String(50), nullable=False)
    APELLIDO = db.Column(db.String(50), nullable=False)
    CORREO = db.Column(db.String(100), nullable=False, unique=True)
    TELEFONO = db.Column(db.String(20))
    APARTAMENTO = db.Column(db.String(10))
    TORRE = db.Column(db.String(10))
    ROL = db.Column(db.Enum('ADMINISTRADOR', 'RESIDENTE', 'PORTERO'), nullable=False)
    ESTADO = db.Column(db.Enum('ACTIVO', 'INACTIVO', 'PENDIENTE'), nullable=False)
    CONTRASENA = db.Column(db.String(255), nullable=False)
    
    # Relaciones principales (del código de tu compañero)
    vehiculos = db.relationship('Vehiculo', back_populates='usuario', cascade="all, delete-orphan")
    reservas = db.relationship('Reserva', back_populates='usuario', cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Usuario {self.CORREO} - {self.ROL}>'

# En models.py - CORREGIR la clase Vehiculo
# En models.py - ACTUALIZAR la clase Vehiculo
# En models.py - ACTUALIZAR la clase Vehiculo
# En models.py - ACTUALIZAR la clase Vehiculo
class Vehiculo(db.Model):
    __tablename__ = 'vehiculo'
    
    ID_VEHICULO = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_USUARIO = db.Column(db.Integer, db.ForeignKey('USUARIO.ID_USUARIO'), nullable=False)
    TIPO = db.Column(db.Enum('CARRO', 'MOTO', 'BICICLETA'), nullable=False)
    PLACA = db.Column(db.String(10), nullable=False, unique=True)
    FECHA_FIN_SOAT = db.Column(db.Date)
    
    # DOCUMENTOS
    DOC_SOAT = db.Column(db.String(255))
    DOC_IDENTIDAD = db.Column(db.String(255))
    DOC_TARJETA_PROPIEDAD = db.Column(db.String(255))
    FECHA_REGISTRO = db.Column(db.DateTime, default=datetime.now)
    ESTADO = db.Column(db.Enum('PENDIENTE', 'APROBADO', 'RECHAZADO'), default='PENDIENTE')
    
    usuario = db.relationship('Usuario', back_populates='vehiculos')
    
    def __repr__(self):
        return f'<Vehiculo {self.PLACA} ({self.TIPO})>'
class Reserva(db.Model):
    __tablename__ = 'reserva'
    
    ID_RESERVA = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_USUARIO = db.Column(db.Integer, db.ForeignKey('USUARIO.ID_USUARIO'), nullable=False)
    NOMBRE = db.Column(db.String(100), nullable=False)  # Aumentado de 50 a 100
    DESCRIPCION = db.Column(db.Text)  # Cambiado de String(255) a Text
    FECHA_HORA = db.Column(db.DateTime, nullable=False)
    COMENTARIO = db.Column(db.String(255))
    ESTADO = db.Column(db.Enum('ACTIVO', 'CANCELADO', 'FINALIZADO', 'EN PROCESO', 'APROBADO'), default='ACTIVO')
    TIPO = db.Column(db.Enum('PUBLICO', 'PRIVADO'), default='PUBLICO')
    CLASE = db.Column(db.Enum('UNICO', 'FRECUENTE', 'RECURRENTE'), default='UNICO')  # Combinado
    
    # Relaciones
    usuario = db.relationship('Usuario', back_populates='reservas')
    inscripciones = db.relationship('InscripcionEvento', back_populates='reserva', cascade="all, delete-orphan")
    recordatorios = db.relationship('RecordatorioEvento', back_populates='reserva', cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Reserva {self.NOMBRE} - {self.ESTADO}>'

class InscripcionEvento(db.Model):
    __tablename__ = 'inscripcion_evento'
    
    ID_RESERVA = db.Column(db.Integer, db.ForeignKey('reserva.ID_RESERVA'), primary_key=True)
    ID_USUARIO = db.Column(db.Integer, db.ForeignKey('USUARIO.ID_USUARIO'), primary_key=True)
    FECHA_INSCRIPCION = db.Column(db.DateTime, default=datetime.now)
    
    # Relaciones
    reserva = db.relationship('Reserva', back_populates='inscripciones')
    usuario = db.relationship('Usuario', backref='inscripciones_eventos')

class RecordatorioEvento(db.Model):
    __tablename__ = 'recordatorio_evento'
    
    ID_RECORDATORIO = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_RESERVA = db.Column(db.Integer, db.ForeignKey('reserva.ID_RESERVA'), nullable=False)
    ID_USUARIO = db.Column(db.Integer, db.ForeignKey('USUARIO.ID_USUARIO'), nullable=False)
    FECHA_ENVIO = db.Column(db.DateTime, nullable=False)
    ESTADO = db.Column(db.Enum('PENDIENTE', 'ENVIADO', 'ERROR'), default='PENDIENTE')  # Mejora del compañero
    
    # Relaciones
    reserva = db.relationship('Reserva', back_populates='recordatorios')
    usuario = db.relationship('Usuario', backref='recordatorios_eventos')

class Sorteo(db.Model):
    __tablename__ = 'sorteo'
    
    ID_SORTEO = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FECHA = db.Column(db.DateTime, default=datetime.now)
    TIPO = db.Column(db.Enum('CARRO', 'MOTO', 'BICICLETA'), nullable=False)
    ID_USUARIO = db.Column(db.Integer, db.ForeignKey('USUARIO.ID_USUARIO'), nullable=False)
    RESULTADO = db.Column(db.Enum('GANADOR', 'ESPERA'), nullable=False)
    
    # Relación
    usuario = db.relationship('Usuario', backref='sorteos')

# --- MODELOS ADICIONALES ---

class Reporte(db.Model):
    __tablename__ = 'REPORTE'
    
    ID_REPORTE = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TITULO = db.Column(db.String(100), nullable=False)
    DETALLE = db.Column(db.Text, nullable=False)
    FECHA_REPORTE = db.Column(db.DateTime, default=datetime.now)
    CREADO_POR = db.Column(db.Integer, db.ForeignKey('USUARIO.ID_USUARIO'), nullable=False)
    
    def __repr__(self):
        return f'<Reporte {self.TITULO}>'

class GestionEspera(db.Model):
    __tablename__ = 'GESTION_ESPERA'
    
    ID_ESPERA = db.Column(db.Integer, primary_key=True, autoincrement=True)
    DETALLE = db.Column(db.Text, nullable=False)
    ESTADO = db.Column(db.Enum('PENDIENTE', 'ATENDIDO'), default='PENDIENTE')
    FECHA_SOLICITUD = db.Column(db.DateTime, default=datetime.now)
    SOLICITADO_POR = db.Column(db.Integer, db.ForeignKey('USUARIO.ID_USUARIO'), nullable=False)
    
    def __repr__(self):
        return f'<GestionEspera {self.ID_ESPERA} - {self.ESTADO}>'

class Evento(db.Model):
    __tablename__ = 'EVENTO'
    
    ID_EVENTO = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TITULO = db.Column(db.String(100), nullable=False)
    DESCRIPCION = db.Column(db.Text, nullable=False)
    FECHA = db.Column(db.DateTime, nullable=False)
    CREADO_POR = db.Column(db.Integer, db.ForeignKey('USUARIO.ID_USUARIO'), nullable=False)
    
    def __repr__(self):
        return f'<Evento {self.TITULO} - {self.FECHA}>'

class PrestamoParqueadero(db.Model):
    __tablename__ = 'PRESTAMO_PARQUEADERO'
    
    ID_PRESTAMO = db.Column(db.Integer, primary_key=True, autoincrement=True)
    VEHICULO = db.Column(db.String(50), nullable=False)
    INICIO = db.Column(db.DateTime, nullable=False)
    FIN = db.Column(db.DateTime, nullable=False)
    RESIDENTE_ID = db.Column(db.Integer, db.ForeignKey('USUARIO.ID_USUARIO'), nullable=False)
    
    def __repr__(self):
        return f'<PrestamoParqueadero {self.VEHICULO}>'

class Anuncio(db.Model):
    __tablename__ = 'ANUNCIO'
    
    ID_ANUNCIO = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TITULO = db.Column(db.String(100), nullable=False)
    MENSAJE = db.Column(db.Text, nullable=False)
    FECHA = db.Column(db.DateTime, default=datetime.now)
    PUBLICADO_POR = db.Column(db.Integer, db.ForeignKey('USUARIO.ID_USUARIO'), nullable=False)
    
    def __repr__(self):
        return f'<Anuncio {self.TITULO}>'

class Recibo(db.Model):
    __tablename__ = 'RECIBO'
    
    ID_RECIBO = db.Column(db.Integer, primary_key=True, autoincrement=True)
    MONTO = db.Column(db.Float, nullable=False)
    FECHA = db.Column(db.DateTime, default=datetime.now)
    PAGADO = db.Column(db.Boolean, default=False)
    RESIDENTE_ID = db.Column(db.Integer, db.ForeignKey('USUARIO.ID_USUARIO'), nullable=False)
    
    def __repr__(self):
        return f'<Recibo {self.ID_RECIBO} - ${self.MONTO}>'

class Actividad(db.Model):
    __tablename__ = 'ACTIVIDAD'
    
    ID_ACTIVIDAD = db.Column(db.Integer, primary_key=True, autoincrement=True)
    DESCRIPCION = db.Column(db.Text, nullable=False)
    FECHA = db.Column(db.DateTime, default=datetime.now)
    USUARIO_ID = db.Column(db.Integer, db.ForeignKey('USUARIO.ID_USUARIO'), nullable=False)
    
    def __repr__(self):
        return f'<Actividad {self.ID_ACTIVIDAD}>'

class Voluntario(db.Model):
    __tablename__ = 'VOLUNTARIO'
    
    ID_VOLUNTARIO = db.Column(db.Integer, primary_key=True, autoincrement=True)
    NOMBRE = db.Column(db.String(100), nullable=False)
    ACTIVIDAD = db.Column(db.String(100), nullable=False)
    DISPONIBILIDAD = db.Column(db.String(50), nullable=False)
    CONTACTO = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'<Voluntario {self.NOMBRE}>'

class Incidente(db.Model):
    __tablename__ = 'INCIDENTE'
    
    ID_INCIDENTE = db.Column(db.Integer, primary_key=True, autoincrement=True)
    DETALLE = db.Column(db.Text, nullable=False)
    FECHA = db.Column(db.DateTime, default=datetime.now)
    REPORTADO_POR = db.Column(db.Integer, db.ForeignKey('USUARIO.ID_USUARIO'), nullable=False)
    
    def __repr__(self):
        return f'<Incidente {self.ID_INCIDENTE}>'

class Paquete(db.Model):
    __tablename__ = 'paquete'
    
    id = db.Column(db.Integer, primary_key=True)
    residente_id = db.Column(db.Integer)
    torre = db.Column(db.String(10), nullable=False)
    apartamento = db.Column(db.String(10), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    remitente = db.Column(db.String(100))
    numero_seguimiento = db.Column(db.String(50))
    fecha_ingreso = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    fecha_notificacion = db.Column(db.TIMESTAMP)
    fecha_entrega = db.Column(db.TIMESTAMP)
    estado = db.Column(db.Enum('recibido', 'notificado', 'entregado'), default='recibido')
    notificado_correo = db.Column(db.Boolean, default=False)
    notificado_whatsapp = db.Column(db.Boolean, default=False)
    observaciones = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Paquete {self.torre}-{self.apartamento}>'