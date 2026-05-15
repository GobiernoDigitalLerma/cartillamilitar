from fastapi import FastAPI, Depends, HTTPException, Request, Form, File, UploadFile, Header
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime, date
import os
import shutil
import asyncio
import json
import io
import pandas as pd

from fastapi_mail import FastMail, MessageSchema
from config import conf

import models, schemas, crud
from database import SessionLocal, engine, Base

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors

from reportlab.lib.colors import HexColor


# ==================== FUNCIÓN PARA GENERAR PDF (FORMATO EXACTO) ====================
def generar_pdf_cartilla_oficial(solicitud_id: int, db: Session):

    solicitud = db.query(models.Solicitud).filter(models.Solicitud.id == solicitud_id).first()
    if not solicitud:
        return None

    os.makedirs("cartillas", exist_ok=True)
    nombre_archivo = f"cartillas/cartilla_{solicitud.numero_registro}.pdf"

    ancho = 306
    alto = 468

    c = canvas.Canvas(nombre_archivo, pagesize=(ancho, alto))
    # Color de fondo (cambia el código hexadecimal por el que quieras)
    c.setFillColor(HexColor("#A39E98"))  # Beige / Crema - Color original SEDENA
    c.rect(0, 0, ancho, alto, fill=1, stroke=0)
    c.setFillColor(colors.black)  # Restaurar color negro para el texto

    # ================= ENCABEZADO CENTRADO =================
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(ancho / 2, alto - 25, "SECRETARÍA DE LA DEFENSA NACIONAL")

    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(ancho / 2, alto - 40, "SERVICIO MILITAR NACIONAL")

    c.setFont("Helvetica", 8)
    c.drawCentredString(ancho / 2, alto - 55, 'CLASE ".........."')

    c.line(20, alto - 60, ancho - 20, alto - 60)

    # ================= CAMPOS =================
    y = alto - 80
    c.setFont("Helvetica", 7)

    def campo(label, valor):
        nonlocal y  # 🔥 ESTA ERA LA CAUSA DEL ERROR

        puntos = "........................................"

        c.drawString(20, y, f"{label} {puntos}")
        c.drawString(95, y, str(valor))

        y -= 16

    campo("Nombre:", solicitud.nombre_completo)
    campo("Fecha de Nacimiento:", solicitud.fecha_nacimiento)
    campo("Nació en:", "Lerma, Estado de México")
    campo("Hijo de:", solicitud.nombre_padre or "")
    campo("Y de:", solicitud.nombre_madre or "")
    campo("Estado Civil:", solicitud.estado_civil or "")
    campo("Ocupación:", solicitud.ocupacion or "")
    campo("¿Sabe leer y escribir?:", "Sí" if solicitud.sabe_leer else "No")
    campo("CURP:", solicitud.curp or "")
    campo("Grado de estudios:", solicitud.grado_estudios or "")
    campo("Domicilio:", solicitud.domicilio or "")

    # ================= SEPARADOR =================
    y -= 5
    c.drawString(20, y, "..................................................................................................................................")

    # ================= FIRMAS =================
    y -= 25
    c.setFont("Helvetica", 6)

    c.drawString(20, y, "Firma del Interesado")
    

    c.drawString(150, y, "Firma del Operador")
    

    y -= 25

    c.drawString(20, y, "El Presidente de la J.M. de R.")
    c.drawString(20, y - 5, "................................")

    c.drawString(150, y, "El Coronel de Artillería")
    y -= 16
    c.drawString(150, y, "Jefe de Reclutamiento")
    # Firma real debajo
    c.drawImage("static/firma.png", 150, y - 10, width=70, height=15, mask='auto')
    # ================= SEPARADOR =================
    y -= 15
    c.line(18, y, ancho - 20, y)  # 🔥 corregido (no usar puntos aquí)

    # ================= FOTO =================
    foto_x = 18
    foto_y = 18

    c.rect(foto_x, foto_y, 65, 95)

    c.setFont("Helvetica", 6)
    c.drawString(foto_x, foto_y + 100, "Fotografía de frente")

    c.setFont("Helvetica", 5)

    texto_foto = [
        "Foto cuadrangular",
        "de 35 x 45 milímetros,",
        "comprendiendo la cabeza",
        "y el cuello, entre el",
        "nacimiento del cabello",
        "y el borde inferior de",
        "la barbilla tendrá",
        "21 milímetros, fondo",
        "blanco y sin retoque."
    ]

    tx = foto_x + 5
    ty = foto_y + 88

    for linea in texto_foto:
        c.drawString(tx, ty, linea)
        ty -= 7

    # ================= HUELLA =================
    huella_x = ancho - 90
    huella_y = 18

    c.rect(huella_x, huella_y, 65, 95)

    c.setFont("Helvetica", 6)
    c.drawString(huella_x, huella_y + 100, "Huella del pulgar derecho")

    # ================= MATRÍCULA =================
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(ancho / 2, 95, "MATRÍCULA Núm.")
    c.drawCentredString(ancho / 2, 82, solicitud.numero_registro)

    # ================= ADVERTENCIA =================
    c.setFont("Helvetica-Bold", 5)
    c.drawCentredString(ancho / 2, 65, "ESTA CARTILLA")
    c.drawCentredString(ancho / 2, 57, "NO DEBE TENER")
    c.drawCentredString(ancho / 2, 49, "RASPUDURAS")

    c.save()
    return nombre_archivo
# ==================== CONFIGURACIÓN INICIAL ====================

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

os.makedirs("files", exist_ok=True)


# ==================== FUNCIONES AUXILIARES ====================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def calcular_edad(fecha):
    hoy = date.today()
    return hoy.year - fecha.year - ((hoy.month, hoy.day) < (fecha.month, fecha.day))


def generar_numero_registro(db: Session):
    año_actual = date.today().year
    ultimo = db.query(models.Solicitud).filter(
        models.Solicitud.numero_registro.like(f'CML-{año_actual}-%')
    ).order_by(models.Solicitud.id.desc()).first()
    
    if ultimo and ultimo.numero_registro:
        partes = ultimo.numero_registro.split('-')
        if len(partes) == 3:
            correlativo = int(partes[2]) + 1
        else:
            correlativo = 1
    else:
        correlativo = 1
    
    return f"CML-{año_actual}-{correlativo:04d}"


def get_current_admin(correo: str, db: Session):
    admin = db.query(models.Administrador).filter(
        models.Administrador.correo == correo
    ).first()
    if not admin:
        raise HTTPException(status_code=401, detail="No autenticado")
    return admin


# ==================== ENDPOINTS PÚBLICOS ====================

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/registro")
async def registro(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    edad = calcular_edad(usuario.fecha_nacimiento)
    if edad < 18:
        raise HTTPException(status_code=400, detail="Debes ser mayor de edad")

    existe = db.query(models.Usuario).filter(models.Usuario.correo == usuario.correo).first()
    
    if existe:
        nuevo_codigo = crud.generar_codigo()
        crud.guardar_codigo(db, existe.id, nuevo_codigo)
        link = f"http://127.0.0.1:8000/verificar-formulario?correo={usuario.correo}&codigo={nuevo_codigo}"
        
        message = MessageSchema(
            subject="🔐 Nuevo código - Cartilla Militar",
            recipients=[usuario.correo],
            body=f"Hola,\n\nTu nuevo código de verificación es: {nuevo_codigo}\n\n👉 Haz clic aquí: {link}\n\nEste código expira en 10 minutos.\n\nSecretaría de la Defensa Nacional",
            subtype="plain"
        )
        fm = FastMail(conf)
        await fm.send_message(message)
        return {"mensaje": f"📧 Se envió un nuevo código a {usuario.correo}"}

    nuevo = crud.crear_usuario(db, usuario.correo, usuario.fecha_nacimiento)
    codigo = crud.generar_codigo()
    crud.guardar_codigo(db, nuevo.id, codigo)
    link = f"http://127.0.0.1:8000/verificar-formulario?correo={usuario.correo}&codigo={codigo}"

    message = MessageSchema(
        subject="🔐 Verificación - Cartilla Militar",
        recipients=[usuario.correo],
        body=f"Hola,\n\nTu código de verificación es: {codigo}\n\n👉 Haz clic aquí: {link}\n\nEste código expira en 10 minutos.\n\nSecretaría de la Defensa Nacional",
        subtype="plain"
    )
    fm = FastMail(conf)
    await fm.send_message(message)
    return {"mensaje": f"📧 Código enviado a {usuario.correo}. Revisa tu correo"}


@app.get("/verificar-formulario")
def verificar_formulario(correo: str, codigo: str, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.correo == correo).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    registro_codigo = db.query(models.CodigoVerificacion).filter(
        models.CodigoVerificacion.usuario_id == usuario.id,
        models.CodigoVerificacion.codigo == codigo,
        models.CodigoVerificacion.usado == False
    ).first()

    if not registro_codigo:
        raise HTTPException(status_code=400, detail="Código inválido o ya usado")

    if registro_codigo.expiracion < datetime.now():
        raise HTTPException(status_code=400, detail="El código ya expiró")

    registro_codigo.usado = True
    usuario.verificado = True
    db.commit()

    return RedirectResponse(url=f"/formulario?correo={correo}")


@app.get("/formulario")
def formulario(request: Request, correo: str, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.correo == correo).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return templates.TemplateResponse("formulario.html", {"request": request, "correo": correo})


@app.post("/guardar-solicitud-completa")
async def guardar_solicitud_completa(
    correo: str = Form(...),
    nombre_completo: str = Form(...),
    curp: str = Form(...),
    fecha_nacimiento: str = Form(...),
    nombre_padre: str = Form(None),
    nombre_madre: str = Form(None),
    estado_civil: str = Form(...),
    ocupacion: str = Form(...),
    sabe_leer: bool = Form(...),
    grado_estudios: str = Form(...),
    domicilio: str = Form(...),
    acta_nacimiento: UploadFile = File(...),
    curp_pdf: UploadFile = File(...),
    comprobante_domicilio: UploadFile = File(...),
    comprobante_estudios: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    usuario = db.query(models.Usuario).filter(models.Usuario.correo == correo).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    existe = db.query(models.Solicitud).filter(models.Solicitud.usuario_id == usuario.id).first()
    if existe:
        raise HTTPException(status_code=400, detail="Ya tienes una solicitud registrada")
    
    fecha_nac = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()
    
    nueva_solicitud = models.Solicitud(
        usuario_id=usuario.id,
        nombre_completo=nombre_completo,
        fecha_nacimiento=fecha_nac,
        curp=curp,
        nombre_padre=nombre_padre,
        nombre_madre=nombre_madre,
        estado_civil=estado_civil,
        ocupacion=ocupacion,
        sabe_leer=sabe_leer,
        grado_estudios=grado_estudios,
        domicilio=domicilio
    )
    
    nueva_solicitud.numero_registro = generar_numero_registro(db)
    
    db.add(nueva_solicitud)
    db.commit()
    db.refresh(nueva_solicitud)
    
    documentos = [
        ("acta_nacimiento", acta_nacimiento),
        ("curp", curp_pdf),
        ("comprobante_domicilio", comprobante_domicilio),
        ("comprobante_estudios", comprobante_estudios)
    ]
    
    for tipo, archivo in documentos:
        extension = archivo.filename.split(".")[-1] if archivo.filename else "pdf"
        nombre_archivo = f"solicitud_{nueva_solicitud.id}_{tipo}.{extension}"
        ruta = f"files/{nombre_archivo}"
        
        with open(ruta, "wb") as buffer:
            shutil.copyfileobj(archivo.file, buffer)
        
        doc_db = models.Documento(
            solicitud_id=nueva_solicitud.id,
            tipo=tipo,
            ruta_archivo=ruta
        )
        db.add(doc_db)
    
    db.commit()
    
    historial = models.Historial(
        solicitud_id=nueva_solicitud.id,
        correo=correo,
        nombre=nombre_completo,
        estado="pendiente",
        detalle=f"Solicitud registrada con número {nueva_solicitud.numero_registro}",
        fecha=date.today(),
        hora=datetime.now().time()
    )
    db.add(historial)
    db.commit()
    
    return {"mensaje": f"✅ Solicitud enviada con éxito. Número: {nueva_solicitud.numero_registro}"}


# ==================== ADMINISTRADORES ====================

@app.post("/crear-admin")
def crear_admin(admin: schemas.AdminCreate, db: Session = Depends(get_db)):
    try:
        rol = getattr(admin, 'rol', 'admin')
        nuevo = crud.crear_admin(db, admin.nombre, admin.correo, admin.password, rol)
        if not nuevo:
            raise HTTPException(status_code=400, detail="El correo ya existe")
        return {"mensaje": "Administrador creado", "admin_id": nuevo.id, "rol": nuevo.rol}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/login-admin")
def login_admin(correo: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    try:
        admin = db.query(models.Administrador).filter(
            models.Administrador.correo == correo
        ).first()
        
        if not admin:
            raise HTTPException(status_code=404, detail="Admin no encontrado")
        
        if not crud.verificar_password(password, admin.password):
            raise HTTPException(status_code=401, detail="Contraseña incorrecta")
        
        return {
            "mensaje": "Login exitoso", 
            "correo": correo,
            "rol": admin.rol,
            "admin_id": admin.id,
            "nombre": admin.nombre
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/login-admin-panel")
def login_admin_panel(request: Request):
    return templates.TemplateResponse("login_admin.html", {"request": request})


@app.get("/crear-admin-panel")
def crear_admin_panel(request: Request):
    return templates.TemplateResponse("crear_admin.html", {"request": request})


@app.get("/admin-solicitudes")
def admin_solicitudes(request: Request):
    return templates.TemplateResponse("admin_solicitudes.html", {"request": request})


@app.get("/api/administradores")
def api_administradores(
    db: Session = Depends(get_db),
    x_admin_correo: str = Header(None)
):
    if not x_admin_correo:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    current_admin = get_current_admin(x_admin_correo, db)
    
    if current_admin.rol != "super_admin":
        raise HTTPException(status_code=403, detail="No autorizado. Se requiere rol super_admin")
    
    admins = crud.obtener_todos_admins(db)
    resultado = []
    for admin in admins:
        resultado.append({
            "id": admin.id,
            "nombre": admin.nombre,
            "correo": admin.correo,
            "rol": admin.rol,
            "fecha_creacion": admin.fecha_creacion.isoformat() if admin.fecha_creacion else None
        })
    return resultado


@app.post("/api/administradores")
def crear_administrador(
    admin_data: schemas.AdminCreate,
    db: Session = Depends(get_db),
    x_admin_correo: str = Header(None)
):
    if not x_admin_correo:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    current_admin = get_current_admin(x_admin_correo, db)
    
    if current_admin.rol != "super_admin":
        raise HTTPException(status_code=403, detail="No autorizado. Se requiere rol super_admin")
    
    rol = admin_data.rol if hasattr(admin_data, 'rol') and admin_data.rol else "admin"
    
    nuevo = crud.crear_admin(db, admin_data.nombre, admin_data.correo, admin_data.password, rol)
    
    if not nuevo:
        raise HTTPException(status_code=400, detail="El correo ya existe")
    
    return {"mensaje": "Administrador creado", "admin_id": nuevo.id, "rol": nuevo.rol}


@app.put("/api/administradores/{admin_id}")
def actualizar_administrador(
    admin_id: int,
    admin_data: schemas.AdminUpdate,
    db: Session = Depends(get_db),
    x_admin_correo: str = Header(None)
):
    if not x_admin_correo:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    current_admin = get_current_admin(x_admin_correo, db)
    
    if current_admin.rol != "super_admin":
        raise HTTPException(status_code=403, detail="No autorizado. Se requiere rol super_admin")
    
    if admin_id == current_admin.id:
        raise HTTPException(status_code=400, detail="No puedes modificarte a ti mismo")
    
    admin = crud.actualizar_admin(
        db, admin_id,
        nombre=admin_data.nombre,
        correo=admin_data.correo,
        password=admin_data.password,
        rol=admin_data.rol
    )
    
    if not admin:
        raise HTTPException(status_code=404, detail="Administrador no encontrado")
    
    return {"mensaje": "Administrador actualizado"}


@app.delete("/api/administradores/{admin_id}")
def eliminar_administrador(
    admin_id: int,
    db: Session = Depends(get_db),
    x_admin_correo: str = Header(None)
):
    if not x_admin_correo:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    current_admin = get_current_admin(x_admin_correo, db)
    
    if current_admin.rol != "super_admin":
        raise HTTPException(status_code=403, detail="No autorizado. Se requiere rol super_admin")
    
    if admin_id == current_admin.id:
        raise HTTPException(status_code=400, detail="No puedes eliminarte a ti mismo")
    
    if crud.eliminar_admin(db, admin_id):
        return {"mensaje": "Administrador eliminado"}
    else:
        raise HTTPException(status_code=404, detail="Administrador no encontrado")


@app.get("/admin-administradores")
def admin_administradores(request: Request):
    return templates.TemplateResponse("admin_administradores.html", {"request": request})


@app.get("/api/solicitudes")
def api_solicitudes(db: Session = Depends(get_db)):
    solicitudes = db.query(models.Solicitud).all()
    resultado = []
    
    for sol in solicitudes:
        usuario = db.query(models.Usuario).filter(models.Usuario.id == sol.usuario_id).first()
        resultado.append({
            "id": sol.id,
            "numero_registro": sol.numero_registro,
            "nombre_completo": sol.nombre_completo,
            "correo": usuario.correo if usuario else "N/A",
            "curp": sol.curp,
            "estatus": sol.estatus,
            "fecha_creacion": sol.fecha_creacion.isoformat() if sol.fecha_creacion else None
        })
    return resultado


@app.get("/api/solicitud/{solicitud_id}")
def api_solicitud_detalle(solicitud_id: int, db: Session = Depends(get_db)):
    solicitud = db.query(models.Solicitud).filter(models.Solicitud.id == solicitud_id).first()
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    
    usuario = db.query(models.Usuario).filter(models.Usuario.id == solicitud.usuario_id).first()
    documentos = db.query(models.Documento).filter(models.Documento.solicitud_id == solicitud_id).all()
    
    return {
        "solicitud": {
            "id": solicitud.id,
            "numero_registro": solicitud.numero_registro,
            "nombre_completo": solicitud.nombre_completo,
            "fecha_nacimiento": solicitud.fecha_nacimiento.isoformat() if solicitud.fecha_nacimiento else None,
            "curp": solicitud.curp,
            "nombre_padre": solicitud.nombre_padre,
            "nombre_madre": solicitud.nombre_madre,
            "estado_civil": solicitud.estado_civil,
            "ocupacion": solicitud.ocupacion,
            "sabe_leer": solicitud.sabe_leer,
            "grado_estudios": solicitud.grado_estudios,
            "domicilio": solicitud.domicilio,
            "estatus": solicitud.estatus
        },
        "correo": usuario.correo if usuario else "N/A",
        "documentos": [{"tipo": doc.tipo, "ruta_archivo": doc.ruta_archivo} for doc in documentos]
    }


@app.put("/api/solicitud/{solicitud_id}/estado")
async def cambiar_estado_solicitud(
    solicitud_id: int, 
    request: Request, 
    db: Session = Depends(get_db)
):
    import json
    
    body = await request.body()
    data = json.loads(body)
    nuevo_estado = data.get("estado")
    fecha_cita = data.get("fecha_cita")
    hora_cita = data.get("hora_cita")
    observaciones = data.get("observaciones")
    
    if nuevo_estado not in ["pendiente", "aprobado", "rechazado"]:
        raise HTTPException(status_code=400, detail="Estado inválido")
    
    solicitud = db.query(models.Solicitud).filter(models.Solicitud.id == solicitud_id).first()
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    
    usuario = db.query(models.Usuario).filter(models.Usuario.id == solicitud.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    estado_anterior = solicitud.estatus
    solicitud.estatus = nuevo_estado
    db.commit()
    
    historial = models.Historial(
        solicitud_id=solicitud.id,
        correo=usuario.correo,
        nombre=solicitud.nombre_completo,
        estado=nuevo_estado,
        detalle=f"Estado cambiado de {estado_anterior} a {nuevo_estado} por administrador",
        fecha=date.today(),
        hora=datetime.now().time()
    )
    db.add(historial)
    db.commit()
    
    if nuevo_estado == "aprobado":
        if not fecha_cita or not hora_cita:
            raise HTTPException(status_code=400, detail="Debes proporcionar fecha y hora de cita")
        
        mensaje_correo = f"Estimado(a) {solicitud.nombre_completo},\n\n✅ Su solicitud de Cartilla Militar ha sido APROBADA.\n\n📅 Fecha de cita: {fecha_cita}\n🕐 Hora de cita: {hora_cita}\n\n📌 Lugar: Secretaría de la Defensa Nacional - Oficinas de Lerma\n\nSecretaría de la Defensa Nacional"
        asunto = "✅ Cita asignada - Cartilla Militar"
    
    elif nuevo_estado == "rechazado":
        if not observaciones:
            observaciones = "Por favor, revise su documentación y vuelva a enviar la solicitud."
        
        mensaje_correo = f"Estimado(a) {solicitud.nombre_completo},\n\n❌ Su solicitud de Cartilla Militar ha sido RECHAZADA.\n\n📋 Correcciones necesarias:\n{observaciones}\n\nSecretaría de la Defensa Nacional"
        asunto = "❌ Correcciones necesarias - Cartilla Militar"
    
    else:
        return {"mensaje": f"Estado actualizado a {nuevo_estado}"}
    
    try:
        message = MessageSchema(
            subject=asunto,
            recipients=[usuario.correo],
            body=mensaje_correo,
            subtype="plain"
        )
        fm = FastMail(conf)
        await fm.send_message(message)
    except Exception as e:
        print(f"❌ Error enviando correo: {e}")
    
    return {"mensaje": f"Solicitud {nuevo_estado}. Correo enviado a {usuario.correo}", "correo_enviado": True}


@app.get("/files/{nombre_archivo}")
def descargar_archivo(nombre_archivo: str):
    ruta_completa = f"files/{nombre_archivo}"
    if not os.path.exists(ruta_completa):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return FileResponse(ruta_completa, media_type="application/pdf", filename=nombre_archivo)


@app.get("/exportar-excel")
def exportar_excel(db: Session = Depends(get_db)):
    solicitudes = db.query(models.Solicitud).all()
    
    datos = []
    for sol in solicitudes:
        usuario = db.query(models.Usuario).filter(models.Usuario.id == sol.usuario_id).first()
        datos.append({
            "ID": sol.id,
            "Número de Registro": sol.numero_registro,
            "Nombre Completo": sol.nombre_completo,
            "Correo Electrónico": usuario.correo if usuario else "N/A",
            "CURP": sol.curp,
            "Fecha de Nacimiento": sol.fecha_nacimiento,
            "Nombre del Padre": sol.nombre_padre,
            "Nombre de la Madre": sol.nombre_madre,
            "Estado Civil": sol.estado_civil,
            "Ocupación": sol.ocupacion,
            "Sabe Leer y Escribir": "Sí" if sol.sabe_leer else "No",
            "Grado de Estudios": sol.grado_estudios,
            "Domicilio": sol.domicilio,
            "Estatus": sol.estatus,
            "Fecha de Solicitud": sol.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S") if sol.fecha_creacion else ""
        })
    
    df = pd.DataFrame(datos)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name="Solicitudes", index=False)
        
        worksheet = writer.sheets["Solicitudes"]
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    output.seek(0)
    nombre_archivo = f"solicitudes_cartilla_{date.today().strftime('%Y%m%d')}.xlsx"
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={nombre_archivo}"}
    )


@app.get("/admin")
def admin(request: Request, db: Session = Depends(get_db)):
    usuarios = db.query(models.Usuario).all()
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "usuarios": usuarios
    })


@app.get("/generar-pdf/{solicitud_id}")
def generar_pdf(solicitud_id: int, db: Session = Depends(get_db)):
    ruta_pdf = generar_pdf_cartilla_oficial(solicitud_id, db)
    
    if not ruta_pdf:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    
    return FileResponse(
        ruta_pdf,
        media_type="application/pdf",
        filename=f"cartilla_militar_{solicitud_id}.pdf"
    )