from django.db import models
import datetime

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.

class Departamento(models.Model):
    Nombre = models.CharField(verbose_name="Departamento",max_length=255)

    def __str__(self):
        return self.Nombre


class Municipio(models.Model):
    Nombre = models.CharField(verbose_name="Municipio", max_length=255)
    Departamento = models.ForeignKey(Departamento, verbose_name="Departamento", default=None, on_delete=models.SET_DEFAULT)

    def __str__(self):
        return "%s, %s" %(self.Nombre, self.Departamento)


class Persona(models.Model):
    Nombres = models.CharField(verbose_name="Nombre(s)", max_length=255, null=False)
    Apellidos = models.CharField(verbose_name="Apellido(s)", max_length=255, null=False)
    Telefono = models.CharField(max_length=20)
    Direccion = models.CharField(max_length=100)
    DPI = models.CharField(max_length=20)
    NIT = models.CharField(max_length=20)

    # REQUIRED_FIELDS = ['Nombres', 'Apellidos', 'Telefono', 'Direccion', 'NIT']

class UsuarioManager(BaseUserManager):
    def create_user(self, Email, Nombres, Apellidos, Telefono, Direccion, DPI, NIT, password=None):
        if not Email:
            raise ValueError("Por favor ingrese un Nombre valido")
        if not Nombres: 
            raise ValueError("Por favor ingrese Nombre")
        if not Apellidos:
            raise ValueError("Por favor ingrese un Apellido")
        if not DPI:
            raise ValueError("Por favor ingrese un Apellido")
        if not Direccion:
            raise ValueError("Por favor ingrese un Apellido")

        nueva_persona = Persona(
            Nombres = Nombres, 
            Apellidos = Apellidos, 
            Telefono = Telefono, 
            Direccion = Direccion, 
            DPI = DPI, 
            NIT = NIT
        )

        nueva_persona.save(using=self._db)

        nuevo_usuario = self.model(
            Email = self.normalize_email(Email),
            Persona = nueva_persona
        )

        nuevo_usuario.set_password(password)
        nuevo_usuario.save(using=self._db)
        return nuevo_usuario
    
    def create_superuser(self, Email, password):

        user = self.create_user(
            Email = self.normalize_email(Email),
            Nombres = "SuperUser", 
            Apellidos = "Admin", 
            Telefono = "Telefono", 
            Direccion = "Direccion", 
            DPI = "DPI", 
            NIT = "NIT",
            password = password
        )

        user.is_admin		= True
        user.is_staff		= True
        user.is_superuser	= True
        
        user.save(using=self._db)
        return user
    

class Usuario(AbstractBaseUser, PermissionsMixin):
    Email           = models.EmailField(verbose_name="email", max_length=90, unique=True)
    Persona         = models.ForeignKey(Persona, on_delete=models.CASCADE)
    date_joined		= models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login		= models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin		= models.BooleanField(default=False)
    is_active		= models.BooleanField(default=True)
    is_staff		= models.BooleanField(default=False)
    is_superuser	= models.BooleanField(default=False)

    USERNAME_FIELD = 'Email'
    

    objects = UsuarioManager()

    def __str__(self):
        return self.Email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_lable):
        return True

class Negocio(models.Model):
    RazonSocial = models.CharField(max_length=255, null=True)
    NombreComercial = models.CharField(max_length=255, null=True)
    NITNegocio = models.CharField(max_length=10, null=True)
    Telefono = models.CharField(max_length=20, null=True)

class Sucursal(models.Model):
    negocio = models.ForeignKey(Negocio, default=None, on_delete=models.SET_DEFAULT, null=False)
    municipio = models.ForeignKey(Municipio, verbose_name="Municipio",default=None, on_delete=models.SET_DEFAULT, null=False )#, default= None, on_delete=models.SET_DEFAULT)
    direccion = models.CharField(max_length=255)

class Owner(models.Model):
    Persona = models.ForeignKey(Persona, default=None, on_delete=models.SET_DEFAULT)
    Sucursal = models.ForeignKey(Sucursal, default=None, on_delete=models.SET_DEFAULT)

class Queja(models.Model):
    IDExterno = models.IntegerField(null=True)
    CorrelativoLibro = models.IntegerField(null=True)
    Folio = models.IntegerField(null=True)
    Activo = models.BooleanField(default=True)
    Sucursal = models.ForeignKey(Sucursal, default=None, on_delete= models.SET_DEFAULT)
    FechaCreacion = models.DateTimeField()
    FechaActualizacion = models.DateTimeField()
    NotificarEmail = models.EmailField(max_length=128, null=True)

class UsuarioQueja(models.Model):
    Usuario = models.ForeignKey(Usuario, verbose_name="Usuario Asignado", default=None, on_delete=models.SET_DEFAULT)
    Queja = models.ForeignKey(Queja, default=None, on_delete=models.SET_DEFAULT)


class TipoAccion(models.Model):
    Nombre = models.CharField(max_length=128)
    Descripcion = models.CharField(max_length=255)
    EsAccionCierre = models.BooleanField()
    

class Accion(models.Model):
    Queja = models.ForeignKey(Queja, default=None, on_delete=models.SET_DEFAULT)
    TipoAccion = models.ForeignKey(TipoAccion, default=None, on_delete=models.SET_DEFAULT)
    Usuario = models.ForeignKey(Usuario, null=True,default=None, on_delete=models.SET_DEFAULT)
    Comentario = models.CharField(max_length=2048)
    FechaCreacion =models.DateTimeField()


