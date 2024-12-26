from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Formulario, Token, Email, Usuario, AdminCredentials, RevisionDeDatos

class UsuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'uapaterno', 'uapmaterno', 'unombre', 'calle', 'numero', 'colonia', 'cp', 'localidad', 'municipio', 'estado','gmail']


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = ('id','email', 'token', 'is_validated')

class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = ['id','email']
class FormularioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Formulario
        fields = [
            'id',
            'a_paterno',
            'a_materno',
            'nombre',
            'fecha_nacimiento',
            'nacio_en',
            'hijo_de',
            'y_de',
            'estado_civil',
            'ocupacion',
            'sabe_leer_escribir',
            'grado_maximo_estudios',
            'domicilio',
            'email',
            'creado_a_las',
            'datos_correctos',
            'fecha_revision',
            'curp'
        ]

    #def create(self, validated_data):
     #   usuario_data = validated_data.pop('usuario')
#
 #       usuario = Usuario.objects.create(**usuario_data)
  #      
   #     formulario = Formulario.objects.create( usuario=usuario, **validated_data)
    #    return formulario

class AdminCredentialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminCredentials
        fields = ['user', 'password']


class RevisionDeDatosSerializer(serializers.ModelSerializer):
    class Meta:
        model = RevisionDeDatos
        fields = '__all__'