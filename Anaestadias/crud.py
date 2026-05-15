from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import models
import random
import datetime
from passlib.context import CryptContext

# Configurar contexto de encriptación
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def encriptar_password(password):
    """Encripta una contraseña usando bcrypt"""
    return pwd_context.hash(password)


def verificar_password(password, hashed):
    """Verifica si una contraseña coincide con su versión encriptada"""
    try:
        return pwd_context.verify(password, hashed)
    except Exception:
        return False


def crear_usuario(db: Session, correo, fecha_nacimiento):
    """Crea un nuevo usuario en la base de datos"""
    try:
        usuario = models.Usuario(
            correo=correo,
            fecha_nacimiento=fecha_nacimiento
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario
    except Exception:
        db.rollback()
        return None


def generar_codigo():
    """Genera un código de verificación de 6 dígitos"""
    return str(random.randint(100000, 999999))


def guardar_codigo(db: Session, usuario_id, codigo):
    """Guarda un código de verificación en la base de datos"""
    try:
        expiracion = datetime.datetime.now() + datetime.timedelta(minutes=10)
        nuevo_codigo = models.CodigoVerificacion(
            usuario_id=usuario_id,
            codigo=codigo,
            expiracion=expiracion,
            usado=False
        )
        db.add(nuevo_codigo)
        db.commit()
        return nuevo_codigo
    except Exception:
        db.rollback()
        return None


def crear_admi(db: Session, nombre, correo, password, rol="admi"):
    """Crea un nuevo administrador con contraseña encriptada y rol específico"""
    try:
        hashed = encriptar_password(password)
        
        nuevo = models.Administrador(
            nombre=nombre,
            correo=correo,
            password=hashed,
            rol=rol
        )
        
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return nuevo
        
    except IntegrityError:
        db.rollback()
        return None
    except Exception:
        db.rollback()
        return None


def obtener_admin_por_correo(db: Session, correo):
    """Obtiene un administrador por su correo electrónico"""
    try:
        admin = db.query(models.Administrador).filter(
            models.Administrador.correo == correo
        ).first()
        return admin
    except Exception:
        return None


def obtener_admin_por_id(db: Session, admin_id):
    """Obtiene un administrador por su ID"""
    try:
        admin = db.query(models.Administrador).filter(
            models.Administrador.id == admin_id
        ).first()
        return admin
    except Exception:
        return None


def obtener_todos_admins(db: Session):
    """Obtiene todos los administradores"""
    try:
        admins = db.query(models.Administrador).all()
        return admins
    except Exception:
        return []


def actualizar_admin(db: Session, admin_id, nombre=None, correo=None, password=None, rol=None):
    """Actualiza los datos de un administrador"""
    try:
        admin = db.query(models.Administrador).filter(models.Administrador.id == admin_id).first()
        if not admin:
            return None
        
        if nombre:
            admin.nombre = nombre
        if correo:
            admin.correo = correo
        if password:
            admin.password = encriptar_password(password)
        if rol:
            admin.rol = rol
        
        db.commit()
        db.refresh(admin)
        return admin
    except Exception:
        db.rollback()
        return None


def eliminar_admin(db: Session, admin_id):
    """Elimina un administrador por su ID"""
    try:
        admin = db.query(models.Administrador).filter(models.Administrador.id == admin_id).first()
        if not admin:
            return False
        
        db.delete(admin)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False


def es_super_admin(db: Session, correo):
    """Verifica si un administrador es superad"""
    try:
        admin = db.query(models.Administrador).filter(
            models.Administrador.correo == correo
        ).first()
        return admin.rol == "super_admin" if admin else False
    except Exception:
        return False


def obtener_usuario_por_correo(db: Session, correo):
    """Obtiene un usuario por su correo electrónico"""
    try:
        usuario = db.query(models.Usuario).filter(
            models.Usuario.correo == correo
        ).first()
        return usuario
    except Exception:
        return None


def obtener_solicitud_por_usuario(db: Session, usuario_id):
    """Obtiene la solicitud de un usuario"""
    try:
        solicitud = db.query(models.Solicitud).filter(
            models.Solicitud.usuario_id == usuario_id
        ).first()
        return solicitud
    except Exception:
        return None


def obtener_solicitud_por_id(db: Session, solicitud_id):
    """Obtiene una solicitud por su ID"""
    try:
        solicitud = db.query(models.Solicitud).filter(
            models.Solicitud.id == solicitud_id
        ).first()
        return solicitud
    except Exception:
        return None