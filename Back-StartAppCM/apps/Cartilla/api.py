from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.mail import EmailMessage, send_mail
import uuid
import logging
logger = logging.getLogger(__name__)
from rest_framework import viewsets
from rest_framework import status


# Importaciones de modelos
from.models import Formulario, Token, Email, Usuario, RevisionDeDatos

# Importaciones de serializers
from .serializer import FormularioSerializer, TokenSerializer, EmailSerializer, UsuSerializer, RevisionDeDatosSerializer

class UsuViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    permission_classes = [permissions.AllowAny] 
    serializer_class = UsuSerializer

class FormularioViewSet(viewsets.ModelViewSet):
    queryset = Formulario.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = FormularioSerializer


class EmailViewSet(viewsets.ModelViewSet):
    queryset = Email.objects.all()
    serializer_class = EmailSerializer

    def create(self, request, *args, **kwargs):
        email_direccion = request.data.get('email')
        
        if not email_direccion:
            return Response({'message': 'El campo email es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)
        
        email, created = Email.objects.get_or_create(email=email_direccion)
        
        if not created:
            # Verificar si el correo ya está validado
            if Token.objects.filter(email=email, is_validated=True).exists():
                return Response({
                    'message': 'El correo electrónico ya está validado',
                    'validated': True
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'message': 'El correo electrónico ya existe, pero no está validado',
                    'validated': False
                }, status=status.HTTP_200_OK)
        
        # Crear y enviar un nuevo token
        token = Token.objects.create(email=email, token=uuid.uuid4().hex[:10])
        email_message = EmailMessage(
            "Mensaje de Ayuntamiento Lerma",
            f"Tu token único es: {token.token}",
            '',
            [email.email]
        )
        
        try:
            email_message.send()
            return Response({'message': 'Correo electrónico enviado correctamente'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response({'message': 'Error al enviar correo electrónico'}, status=status.HTTP_400_BAD_REQUEST)

class TokenViewSet(viewsets.ModelViewSet):
    queryset = Token.objects.all()
    serializer_class = TokenSerializer

    def create(self, request, *args, **kwargs):
        email_address = request.data.get('email')
        if not email_address:
            return Response({'message': 'El campo email es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            email = Email.objects.get(email=email_address)
        except Email.DoesNotExist:
            return Response({'message': 'El correo electronico no existe'}, status=status.HTTP_400_BAD_REQUEST)
        
        token = Token.objects.create(email=email, token=uuid.uuid4().hex[:10])
        return Response(self.serializer_class(token).data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False)
    def validacion(self, request, *args, **kwargs):
        token = request.data.get('token')
        if not token:
            return Response({'message': 'El campo token es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token_obj = Token.objects.get(token=token)
            if token_obj:
                token_obj.is_validated = True
                token_obj.save()
                return Response({'message': 'Token valido', 'email': token_obj.email.email}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({'message': 'Token invalido'}, status=status.HTTP_400_BAD_REQUEST)
        

#Envio de los datos correctos
class RevisionDeDatosViewSet(viewsets.ModelViewSet):
    queryset = RevisionDeDatos.objects.all()
    serializer_class = RevisionDeDatosSerializer

    def perform_create(self, serializer):
        revision = serializer.save()

        asunto_fijo = "Revisión de Datos Cartilla Militar Lerma México 2024"

        mensaje = (
            f"Hola,\n\n"
            f"Sus datos han sido verificados y son correctos. "
            f"Por favor, acuda a la oficina durante el período del {revision.fecha_inicio.strftime('%d de %B de %Y')} "
            f"al {revision.fecha_limite.strftime('%d de %B de %Y')}.\n\n"
            f"Detalles de la revisión:\n"
            f"Mensaje: {revision.mensaje}\n\n"
            f"Atentamente,\n"
            f"El equipo de revisión de datos"
        )

        send_mail(
            subject=asunto_fijo,
            message=mensaje,
            from_email='tu_correo@example.com', #MODIFICACIÓN DE CORREO, UNO PROPIO
            recipient_list=[revision.email],
            fail_silently=False,
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        email = request.query_params.get('email')
        if email:
            queryset = self.queryset.filter(email=email)
            if not queryset.exists():
                return Response({'error': 'No se encontraron datos para este correo electrónico.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        return super().list(request, *args, **kwargs)