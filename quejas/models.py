from django.db import models
import datetime

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.

class Region(models.Model):
    nombre = models.CharField(verbose_name="Region",max_length=255)

    def __str__(self):
        return "Region %s" %(self.nombre)

class Departamento(models.Model):
    nombre = models.CharField(verbose_name="Departamento",max_length=255)
    region = models.ForeignKey(Region, verbose_name="Region", default=None, on_delete=models.SET_DEFAULT)

    def __str__(self):
        return "%s, %s" %(self.nombre, self.region)


class Municipio(models.Model):
    nombre = models.CharField(verbose_name="Municipio", max_length=255)
    departamento = models.ForeignKey(Departamento, verbose_name="Departamento", default=None, on_delete=models.SET_DEFAULT)

    def __str__(self):
        return "%s, %s" %(self.nombre, self.departamento)


class Persona(models.Model):
    nombres = models.CharField(verbose_name="Nombre(s)", max_length=255, null=False)
    apellidos = models.CharField(verbose_name="Apellido(s)", max_length=255, null=False)
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=100)
    dpi = models.CharField(max_length=20)
    nit = models.CharField(max_length=20)

    # REQUIRED_FIELDS = ['Nombres', 'Apellidos', 'Telefono', 'Direccion', 'NIT']

class UsuarioManager(BaseUserManager):
    def create_user(self, email, nombres, apellidos, telefono, direccion, dpi, nit, password=None):
        if not email:
            raise ValueError("Por favor ingrese un Nombre valido")
        if not nombres: 
            raise ValueError("Por favor ingrese Nombre")
        if not apellidos:
            raise ValueError("Por favor ingrese un Apellido")
        if not dpi:
            raise ValueError("Por favor ingrese un Apellido")
        if not direccion:
            raise ValueError("Por favor ingrese un Apellido")

        nueva_persona = Persona(
            nombres = nombres, 
            apellidos = apellidos, 
            telefono = telefono, 
            direccion = direccion, 
            dpi = dpi, 
            nit = nit
        )

        nueva_persona.save(using=self._db)

        nuevo_usuario = self.model(
            email = self.normalize_email(email),
            persona = nueva_persona
        )

        nuevo_usuario.set_password(password)
        nuevo_usuario.save(using=self._db)
        return nuevo_usuario
    
    def create_superuser(self, email, password):

        user = self.create_user(
            email = self.normalize_email(email),
            nombres = "SuperUser", 
            apellidos = "Admin", 
            telefono = "Telefono", 
            direccion = "Direccion", 
            dpi = "DPI", 
            nit = "NIT",
            password = password
        )

        user.is_admin		= True
        user.is_staff		= True
        user.is_superuser	= True
        
        user.save(using=self._db)
        return user
    

class Usuario(AbstractBaseUser, PermissionsMixin):
    email           = models.EmailField(verbose_name="email", max_length=90, unique=True)
    persona         = models.ForeignKey(Persona, on_delete=models.CASCADE)
    date_joined		= models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login		= models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin		= models.BooleanField(default=False)
    is_active		= models.BooleanField(default=True)
    is_staff		= models.BooleanField(default=False)
    is_superuser	= models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    

    objects = UsuarioManager()

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_lable):
        return True

class Negocio(models.Model):
    razon_social = models.CharField(max_length=255, null=True)
    nombre_comercial = models.CharField(max_length=255, null=True)
    nit_negocio = models.CharField(max_length=10, null=True)
    telefono = models.CharField(max_length=20, null=True)

    def __str__(self):
        return self.nombre_comercial

class Sucursal(models.Model):
    negocio = models.ForeignKey(Negocio, default=None, on_delete=models.SET_DEFAULT, null=False)
    municipio = models.ForeignKey(Municipio, verbose_name="Municipio",default=None, on_delete=models.SET_DEFAULT, null=False )#, default= None, on_delete=models.SET_DEFAULT)
    direccion = models.CharField(max_length=255)

class Owner(models.Model):
    persona = models.ForeignKey(Persona, default=None, on_delete=models.SET_DEFAULT)
    sucursal = models.ForeignKey(Sucursal, default=None, on_delete=models.SET_DEFAULT)

class Queja(models.Model):
    id_xterno = models.IntegerField(null=True)
    correlativo_libro = models.IntegerField(null=True)
    folio = models.IntegerField(null=True)
    activo = models.BooleanField(default=True)
    sucursal = models.ForeignKey(Sucursal, default=None, on_delete= models.SET_DEFAULT)
    fecha_creacion = models.DateTimeField()
    fecha_actualizacion = models.DateTimeField()
    notificar_email = models.EmailField(max_length=128, null=True)

class UsuarioQueja(models.Model):
    usuario = models.ForeignKey(Usuario, verbose_name="Usuario Asignado", default=None, on_delete=models.SET_DEFAULT)
    queja = models.ForeignKey(Queja, default=None, on_delete=models.SET_DEFAULT)


class TipoAccion(models.Model):
    nombre = models.CharField(max_length=128)
    descripcion = models.CharField(max_length=255)
    es_accion_cierre = models.BooleanField()
    

class Accion(models.Model):
    queja = models.ForeignKey(Queja, default=None, on_delete=models.SET_DEFAULT)
    tipo_accion = models.ForeignKey(TipoAccion, default=None, on_delete=models.SET_DEFAULT)
    usuario = models.ForeignKey(Usuario, null=True,default=None, on_delete=models.SET_DEFAULT)
    comentario = models.CharField(max_length=2048)
    fecha_creacion =models.DateTimeField()


