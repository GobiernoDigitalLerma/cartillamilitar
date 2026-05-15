from pydantic import BaseModel
from datetime import date
from typing import Optional

class UsuarioCreate(BaseModel):
    correo: str
    fecha_nacimiento: date


class AdminCreate(BaseModel):
    nombre: str
    correo: str
    password: str
    rol: Optional[str] = "admin"  # Nuevo campo


class AdminUpdate(BaseModel):
    nombre: Optional[str] = None
    correo: Optional[str] = None
    password: Optional[str] = None
    rol: Optional[str] = None


class VerificarCodigo(BaseModel):
    correo: str
    codigo: str


class SolicitudCreate(BaseModel):
    correo: str
    nombre_completo: str
    curp: str
    fecha_nacimiento: date
    nombre_padre: Optional[str] = None
    nombre_madre: Optional[str] = None
    estado_civil: str
    ocupacion: str
    sabe_leer: bool
    grado_estudios: str
    domicilio: str