from django.db import models

class TipoAnimal(models.Model):
    nombre = models.CharField(max_length=100)
    def __str__(self):
        return f"Tipo de Animal: {self.nombre}"