from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.mail import send_mail
from django.contrib import messages
from django.forms import inlineformset_factory

#model related imports
from quejas.models import *
from django.core.exceptions import ObjectDoesNotExist


#auth related imports
from django.contrib.auth.decorators import *
from django.contrib.auth import authenticate, login, logout

#form related imports
from django.contrib.auth.forms import UserCreationForm
from quejas.forms import *
from . import forms


# Create your views here.
def busqueda_municipio(request):
    return render(request, "index.html")

def index(request):
    return render(request, "index.html")

def view_ingreso_queja(request):
    if request.method == "POST":
        formulario = ingreso_queja(data=request.POST)

        if formulario.is_valid():
            form_limpio=formulario.cleaned_data

            
            var_municipio = Municipio.objects.get(id = form_limpio['CampoMunicipio'].id)

            try:
                var_negocio = Negocio.objects.get(NombreComercial=form_limpio["CampoNombreComercial"])
            except ObjectDoesNotExist:
                var_negocio = Negocio.objects.create(NombreComercial=form_limpio["CampoNombreComercial"])

            try:
                var_sucursal = Sucursal.objects.get(municipio=var_municipio,
                direccion=form_limpio["Direccion"],
                negocio=var_negocio)
            except ObjectDoesNotExist:
                var_sucursal = Sucursal.objects.create(municipio=var_municipio,
                direccion=form_limpio["Direccion"],
                negocio=var_negocio)

            var_queja = Queja.objects.create(Sucursal=var_sucursal, 
                FechaCreacion=datetime.datetime.now(), 
                FechaActualizacion=datetime.datetime.now(),
                NotificarEmail=form_limpio["Email"])
        
            ver_accion = Accion.objects.create(
                Comentario=form_limpio["TextoQueja"],
                FechaCreacion=datetime.datetime.now(),
                Queja=var_queja,
                TipoAccion=TipoAccion.objects.get(Nombre="creacion")                
                )

            messages.success(request,'Queja ingresada con éxito. Numero de Queja: %s' %(var_queja.id))

    if request.method == "GET":
        
        formulario = ingreso_queja()
        
    contexto = {"formulario":formulario}
    return render(request, "ingreso_queja.html", contexto)

def view_logout_usuario(request):
    logout(request)
    return redirect('index')

def login_usuario(request):

    if request.method == "POST":
        formulario = login_form(request.POST)


        email_usuario = request.POST.get('username') #formulario['username']
        password = request.POST.get('password') #formulario['password']

        user = authenticate(request, username=email_usuario, password=password)

        if user is None:
            messages.error(request, 'No se pudo ingresar con esos datos')

        else:
            login(request=request, user=user)
            messages.success(request, 'Bienvenido usuario')
            return redirect('index')

    if request.method == "GET":
        
        formulario = login_form()

    return render(request, "login_usuario.html", {"formulario":formulario})

def ver_municipios(request):
    tabla_municipios = Municipio.objects.all()

    filas = []

    for municipio in tabla_municipios:
        filas.append([municipio.Nombre, municipio.Departamento.Nombre])
    

    tabla_datos = {"encabezado":["Municipio","Departamento"],"filas":filas}

    context = {"tabla":tabla_datos}

    return render(request, "lista_municipios.html", context)

# def mostrar_quejas(request):
