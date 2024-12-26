from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



class Email(models.Model):
    email = models.EmailField(unique=True)

class Token(models.Model):
    email           = models.ForeignKey(Email, on_delete=models.CASCADE)
    token           = models.CharField(max_length=10, unique=True)
    is_validated    = models.BooleanField(default=False)
    
class Usuario(models.Model):
    uapaterno           = models.CharField(max_length=15)
    uapmaterno          = models.CharField(max_length=15)
    unombre             = models.CharField(max_length=30)
    calle               = models.CharField(max_length=50)
    numero              = models.PositiveIntegerField()
    colonia             = models.CharField(max_length=60)
    cp                  = models.PositiveIntegerField()
    localidad           = models.CharField(max_length=20)
    municipio           = models.CharField(max_length=20)
    estado              = models.CharField(max_length=20)
    gmail = models.CharField(max_length=100, default='example@gmail.com')


class Formulario(models.Model):
    a_paterno             = models.CharField(max_length=100)
    a_materno             = models.CharField(max_length=100)
    nombre                = models.CharField(max_length=100)
    fecha_nacimiento      = models.DateField()
    nacio_en              = models.CharField(max_length=100)
    hijo_de               = models.CharField(max_length=100)
    y_de                  = models.CharField(max_length=100, null=True, blank=True)
    estado_civil          = models.CharField(max_length=100)
    ocupacion             = models.CharField(max_length=100)
    sabe_leer_escribir    = models.BooleanField(null=True, blank=True)
    curp                  = models.CharField(max_length=18, null=True, blank=True)
    grado_maximo_estudios = models.CharField(max_length=100)
    domicilio             = models.CharField(max_length=100)
    email                 = models.EmailField(max_length=100)
    creado_a_las          = models.DateTimeField(auto_now_add=True)
    datos_correctos       = models.BooleanField(default=False) 
    fecha_revision = models.DateTimeField(null=True, blank=True)

    # Funcion para imprimir el nombre
    def __str__(self):
        return f'{self.nombre} {self.a_paterno} {self.a_materno}'


class AdminCredentials(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.user.username
    

class RevisionDeDatos(models.Model):
    email = models.EmailField(max_length=100)
    asunto = models.CharField(max_length=200, default='Asunto predeterminado')
    mensaje = models.TextField()
    fecha_inicio = models.DateTimeField()
    fecha_limite = models.DateTimeField()
    creado_a_las = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email