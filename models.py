from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, ForeignKey, Enum, Text, Time
from database import Base
import datetime

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    correo = Column(String(100), unique=True)
    fecha_nacimiento = Column(Date)
    verificado = Column(Boolean, default=False)
    fecha_registro = Column(DateTime, default=datetime.datetime.utcnow)


class CodigoVerificacion(Base):
    __tablename__ = "codigos_verificacion"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    codigo = Column(String(10))
    expiracion = Column(DateTime)
    usado = Column(Boolean, default=False)


class Administrador(Base):
    __tablename__ = "administradores"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    correo = Column(String(100), unique=True)
    password = Column(String(255))
    rol = Column(Enum('super_admin', 'admin'), default='admin')
    fecha_creacion = Column(DateTime, default=datetime.datetime.utcnow)


class Solicitud(Base):
    __tablename__ = "solicitudes"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))

    numero_registro = Column(String(50))
    nombre_completo = Column(String(150))
    fecha_nacimiento = Column(Date)
    
    curp = Column(String(20))
    nombre_padre = Column(String(150))
    nombre_madre = Column(String(150))
    
    estado_civil = Column(String(50))
    ocupacion = Column(String(100))
    sabe_leer = Column(Boolean)
    
    grado_estudios = Column(String(100))
    domicilio = Column(Text)
    
    estatus = Column(Enum('pendiente', 'aprobado', 'rechazado'), default='pendiente')
    fecha_creacion = Column(DateTime, default=datetime.datetime.utcnow)


class Documento(Base):
    __tablename__ = "documentos"

    id = Column(Integer, primary_key=True)
    solicitud_id = Column(Integer, ForeignKey("solicitudes.id"))
    tipo = Column(String(50))
    ruta_archivo = Column(String(255))
    fecha_subida = Column(DateTime, default=datetime.datetime.utcnow)


class Historial(Base):
    __tablename__ = "historial"

    id = Column(Integer, primary_key=True)
    solicitud_id = Column(Integer, ForeignKey("solicitudes.id"))

    correo = Column(String(100))
    nombre = Column(String(150))

    estado = Column(Enum('pendiente', 'aprobado', 'rechazado'))
    detalle = Column(Text)

    fecha = Column(Date)
    hora = Column(Time)