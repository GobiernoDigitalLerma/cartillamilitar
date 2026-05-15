from rest_framework import routers
from. api import FormularioViewSet, TokenViewSet, EmailViewSet, FormularioViewSet,UsuViewSet, RevisionDeDatosViewSet
from django.urls import path, include
from . import api


# URLS de el proyecto a usar
router = routers.DefaultRouter()
router.register(r'api/formulario', FormularioViewSet, basename='formulario')
router.register(r'api/usuario', UsuViewSet, basename='usuario')
router.register(r'api/email', EmailViewSet, basename='email')
router.register(r'api/token', TokenViewSet, basename='token')
router.register(r'revision-datos', RevisionDeDatosViewSet, basename='revison-datos')


urlpatterns = [
    path('', include(router.urls)),
    path('validacion/', TokenViewSet.as_view, name='validacion'),
]

urlpatterns = router.urls