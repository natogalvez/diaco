"""diaco URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from quejas import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index, name='index'),
    path('/',views.index, name='index'),
    path("index",views.index, name='index'),
    path("index/",views.index, name='index'),
    path("login/",views.login_usuario, name = 'login'),
    path("ingreso_queja", views.view_ingreso_queja, name ='ingreso_queja'),
    path("ingreso_queja/", views.view_ingreso_queja, name ='ingreso_queja'),
    path("buscar_queja", views.view_buscar_queja, name ='buscar_queja'),
    path("buscar_queja/", views.view_buscar_queja, name ='buscar_queja'),
    path("buscar_queja_anon", views.view_buscar_queja_anon, name ='buscar_queja_anon'),
    path("buscar_queja_anon/", views.view_buscar_queja_anon, name ='buscar_queja_anon'),
    path("mostrar_accion/<int:accion_id>", views.view_mostrar_accion),
    path("mostrar_accion/<int:accion_id>/", views.view_mostrar_accion),
    path("logout/", views.view_logout_usuario, name ='logout'),
    path("municipios/", views.ver_municipios, name ='municipios'),
    #path('buscar/', views.buscar),
    #path("contacto/", views.contacto),
    
]
