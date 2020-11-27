from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate, logout

from quejas.models import *

from django.forms import ModelForm, Select, ModelChoiceField
from django import forms

   
class login_form(AuthenticationForm):
    class Meta:
        model = Usuario
        fields = ['email','password']
        
    username = forms.EmailField(label="")
    username.widget = forms.TextInput(attrs={"type":"email", "class":"form-control", "placeholder":"Correo electrónico", "required":True})

    password = forms.CharField(label="")
    password.widget = forms.PasswordInput(attrs={"class":"form-control", "placeholder":"Contraseña", "required":True})
    
class ingreso_queja(forms.Form):

    Email = forms.EmailField(label="Correo Electrónico",required=False)
    Email.widget = forms.TextInput(attrs={"type":"email", "class":"form-control", "placeholder":"Opcional"})
    
    CampoNombreComercial = forms.CharField(label="Nombre del negocio o comercio")
    CampoNombreComercial.widget = forms.TextInput(attrs={"type":"text", "class":"form-control", "placeholder":"", "required":True})

    Direccion = forms.CharField(label="Direccion del comercio")
    Direccion.widget = forms.TextInput(attrs={"type":"text", "class":"form-control", "placeholder":"", "required":True})

    CampoMunicipio = forms.ModelChoiceField(label="Municipio",  queryset=Municipio.objects.all())

    TextoQueja = forms.CharField(label="Escriba su queja")
    TextoQueja.widget = forms.Textarea(attrs={"type":"text", "class":"form-control", "placeholder":"", "required":True})

class form_buscar_queja(forms.Form):

    num_queja = forms.CharField(label="Ingresa tu número de queja")
    num_queja.widget = forms.TextInput(attrs={"type":"text", "class":"form-control", "placeholder":"Número de queja", "required":True})


class form_editar_queja(forms.Form):

    num_queja = forms.CharField(label="Numero de Queja", disabled=True)
    num_queja.widget = forms.TextInput(attrs={"type":"text", "class":"form-control", "placeholder":"Correo electrónico", "required":True})

    email = forms.EmailField(label="Email", disabled=True)
    email.widget = forms.TextInput(attrs={"type":"email", "class":"form-control", "placeholder":"", "required":True})

    negocio = forms.CharField(label="Nombre del negocio:")
    negocio.widget = forms.TextInput(attrs={"type":"text", "class":"form-control", "placeholder":"Nombre del negocio", "required":True})

    direccion = forms.CharField(label="Dirección del negocio:")
    direccion.widget = forms.TextInput(attrs={"type":"text", "class":"form-control", "placeholder":"Dirección del negocio", "required":True})

    municipio = forms.CharField(label="Municipio, Departamento", disabled=True)
    direccion.widget = forms.TextInput(attrs={"type":"text", "class":"form-control", "placeholder":"", "required":True})






