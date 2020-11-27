from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.mail import send_mail
from django.contrib import messages
from django.forms import inlineformset_factory

#model related imports
from quejas.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection


#auth related imports
from django.contrib.auth.decorators import login_required
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
                var_negocio = Negocio.objects.get(nombre_comercial=form_limpio["CampoNombreComercial"])
            except ObjectDoesNotExist:
                var_negocio = Negocio.objects.create(nombre_comercial=form_limpio["CampoNombreComercial"])

            try:
                var_sucursal = Sucursal.objects.get(municipio=var_municipio,
                direccion=form_limpio["Direccion"],
                negocio=var_negocio)
            except ObjectDoesNotExist:
                var_sucursal = Sucursal.objects.create(municipio=var_municipio,
                direccion=form_limpio["Direccion"],
                negocio=var_negocio)

            var_queja = Queja.objects.create(sucursal=var_sucursal, 
                fecha_creacion=datetime.datetime.now(), 
                fecha_actualizacion=datetime.datetime.now(),
                notificar_email=form_limpio["Email"])
        
            ver_accion = Accion.objects.create(
                comentario=form_limpio["TextoQueja"],
                fecha_creacion=datetime.datetime.now(),
                queja=var_queja,
                tipo_accion=TipoAccion.objects.get(nombre="creacion")                
                )

            messages.success(request,'Queja ingresada con éxito. Numero de Queja: %s' %(var_queja.id))

    if request.method == "GET":
        
        formulario = ingreso_queja()
        
    contexto = {"formulario":formulario}
    return render(request, "ingreso_queja.html", contexto)

@login_required(login_url='login')
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

#@login_required(login_url='login')
def view_buscar_queja(request):

    if request.method == "POST":

        formulario = form_buscar_queja(data=request.POST)

        if formulario.is_valid():
            form_limpio=formulario.cleaned_data

            var_queja=None

            try:
                var_queja= Queja.objects.get(id=form_limpio['num_queja'])
            except ObjectDoesNotExist:
                messages.error(request,'La queja con numero %s no existe' %(form_limpio['num_queja']))
            

            if var_queja:

                tabla_acciones = Accion.objects.filter(queja=var_queja.id)

                filas = []

                if tabla_acciones:
                    for accion in tabla_acciones:
                        
                        fila = [accion.id, accion.tipo_accion.descripcion, accion.fecha_creacion]
                        if request.user.is_authenticated:
                            if accion.usuario: var_email = accion.usuario.email
                            else: var_email = ""
                            fila.append(var_email)
                        
                        filas.append(fila)

                    nombres_campos = ["id", "tipo_accion","fecha"]
                    encabezado = ["Numero de Accion", "Tipo de Acción","Fecha de acción"]
                    if request.user.is_authenticated: encabezado.append("Usuario")
                    tabla_datos = {"encabezado":encabezado,"filas":filas}

                    contexto={"queja":var_queja,"tabla":tabla_datos, "nombres_campos":nombres_campos}

                    return render(request, "queja_individual.html", contexto)

                else:
                    messages.error(request,'Ocurrio un error obteniendo las acciones de %s' %(form_limpio['num_queja']))
            
    elif request.method == "GET":
        
        formulario = form_buscar_queja()
        
    
    contexto = {"formulario":formulario,"titulo_seccion":"Busqueda de quejas"}
    return render(request, "busqueda_queja_individual.html", contexto)


def view_mostrar_accion(request,accion_id):

        var_accion = None
        
        try:
            var_accion = Accion.objects.get(id=accion_id)
        except ObjectDoesNotExist:
            messages.error(request,'Hubo un error y no existe esta accion')

        contexto = {"accion":var_accion,"titulo_seccion":"Busqueda de quejas"}

        return render(request, "accion_individual.html",contexto)

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def correr_sql(query,args=None):
    with connection.cursor() as cursor:
        cursor.execute(query,args)
        query_set_data = cursor.fetchall()

    return query_set_data

@login_required(login_url='login')
def view_consulta_queja(request,tipo,parent_id=None):

    if tipo == "region":

        var_quejas_regiones =  correr_sql(query="select qr.id, qr.nombre , count(qq.id) as total from quejas_queja qq join quejas_sucursal qs on qq.sucursal_id = qs.id join quejas_municipio qm on qs.municipio_id = qm.id join quejas_departamento qd on qm.departamento_id = qd.id join quejas_region qr on qd.region_id = qr.id group by qr.id, qr.nombre")

        if var_quejas_regiones:
            encabezado = ["Id Region", "Region", "Total"]
            
            tabla_datos = {"encabezado":encabezado,"filas":var_quejas_regiones}

            contexto={"tabla":tabla_datos, "tipo":"region", "titulo_seccion":"Quejas por region"}

            return render(request, "resultados_quejas.html", contexto)

        else:
            messages.error(request,'Ocurrio un error obteniendo los datos, por favor intente de nuevo')
    
    elif tipo == "departamento":

        if parent_id:
            var_quejas_regiones =  correr_sql(query="select qd.id, qd.nombre , count(qq.id) as total from quejas_queja qq join quejas_sucursal qs on qq.sucursal_id = qs.id join quejas_municipio qm on qs.municipio_id = qm.id join quejas_departamento qd on qm.departamento_id = qd.id join quejas_region qr on qd.region_id = qr.id where qr.id = %s group by qd.id, qd.nombre" , args=[parent_id])
        
        else:
            var_quejas_regiones =  correr_sql(query="select qd.id, qd.nombre , count(qq.id) as total from quejas_queja qq join quejas_sucursal qs on qq.sucursal_id = qs.id join quejas_municipio qm on qs.municipio_id = qm.id join quejas_departamento qd on qm.departamento_id = qd.id group by qd.nombre")

        if var_quejas_regiones:
            encabezado = ["Id Departamento", "Departamento", "Total"]
            
            tabla_datos = {"encabezado":encabezado,"filas":var_quejas_regiones}

            contexto={"tabla":tabla_datos, "tipo":"departamento", "titulo_seccion":"Quejas por departamento"}

            return render(request, "resultados_quejas.html", contexto)

        else:
            messages.error(request,'Ocurrio un error obteniendo los datos, por favor intente de nuevo')
    
    elif tipo == "municipio":

        if parent_id:
            var_quejas_regiones =  correr_sql(query="select qm.id, qm.nombre , count(qq.id) as total from quejas_queja qq join quejas_sucursal qs on qq.sucursal_id = qs.id join quejas_municipio qm on qs.municipio_id = qm.id join quejas_departamento qd on qm.departamento_id = qd.id where qd.id = %s group by qm.id, qm.nombre" , args=[parent_id])
        
        else:
            var_quejas_regiones =  correr_sql(query="select qm.id, qm.nombre , count(qq.id) as total from quejas_queja qq join quejas_sucursal qs on qq.sucursal_id = qs.id join quejas_municipio qm on qs.municipio_id = qm.id group by qd.nombre")

        if var_quejas_regiones:
            encabezado = ["Id Municipio", "Municipio", "Total"]
            
            tabla_datos = {"encabezado":encabezado,"filas":var_quejas_regiones}

            contexto={"tabla":tabla_datos, "tipo":"municipio", "titulo_seccion":"Quejas por municipio"}

            return render(request, "resultados_quejas.html", contexto)

        else:
            messages.error(request,'Ocurrio un error obteniendo los datos, por favor intente de nuevo')
    

    elif tipo == "comercio":

        if parent_id:
            var_quejas_regiones =  correr_sql(query="select qn.id, qn.nombre_comercial , count(qq.id) as total from quejas_queja qq join quejas_sucursal qs on qq.sucursal_id = qs.id join quejas_negocio qn on qs.negocio_id = qn.id join quejas_municipio qm on qs.municipio_id = qm.id where qm.id = %s group by qn.id, qn.nombre_comercial" , args=[parent_id])
        
        else:
            var_quejas_regiones =  correr_sql(query="select qn.id, qm.nombre , count(qq.id) as total from quejas_queja qq join quejas_sucursal qs on qq.sucursal_id = qs.id join quejas_municipio qm on qs.municipio_id = qm.id group by qd.nombre")

        if var_quejas_regiones:
            encabezado = ["Id Comercio", "Comercio", "Total"]
            
            tabla_datos = {"encabezado":encabezado,"filas":var_quejas_regiones}

            contexto={"tabla":tabla_datos, "tipo":"comercio", "titulo_seccion":"Quejas por negocio"}

            return render(request, "resultados_quejas.html", contexto)

        else:
            messages.error(request,'Ocurrio un error obteniendo los datos, por favor intente de nuevo')


        """

        elif tipo == "comercio":

        else:
            messages.error(request, message="El tipo de consulta ingresado no es válido")
            return redirect('index')
            """