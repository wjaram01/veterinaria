from django.db import models

# Create your models here.
class Persona(models.Model):
    nombre_completo = models.CharField(max_length=100)
    identificacion = models.CharField(max_length=10, unique=True)
    email = models.EmailField(max_length=50)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    usuario = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='usuario')

    def __str__(self):
        return self.nombre_completo + " - " + self.identificacion
    
    def es_doctor(self):
        return Doctor.objects.filter(persona=self).exists()
    
    def es_cliente(self):
        return Cliente.objects.filter(persona=self).exists()
    
class Cliente(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
    doctor = models.ForeignKey('login.Doctor', on_delete=models.SET_NULL, null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cliente: {self.persona.nombre_completo}"

    def get_count_mascot(self):
        return Mascota.objects.filter(cliente=self).count()
    
    def has_mascot(self):
        return Mascota.objects.filter(cliente=self).exists()

class Doctor(models.Model):
    persona = models.OneToOneField(Persona, on_delete=models.CASCADE)
    especialidad = models.CharField(max_length=100)

    def __str__(self):
        return f"Doctor: {self.persona.nombre_completo} - Especialidad: {self.especialidad}"
    
class Mascota(models.Model):
    archivo = models.FileField(upload_to='documentos/%Y/%m/', verbose_name='Archivo adjunto', null=True, blank=True)
    nombre = models.CharField(max_length=100)
    especie = models.CharField(max_length=50)
    raza = models.CharField(max_length=50, blank=True, null=True)
    edad = models.IntegerField()
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)

    def __str__(self):
        return f"Mascota: {self.nombre} ({self.especie})"
    
    def has_diag(self):
        return self.diagnosticomascota_set.all().exists()
    

class DiagnosticoMascota(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    nombre = models.CharField(max_length=100)
    archivo = models.FileField(upload_to='documentos/%Y/%m/', verbose_name='Archivo adjunto', null=True, blank=True)

