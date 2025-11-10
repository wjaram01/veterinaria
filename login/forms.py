# blog/forms.py (o mi_app/forms.py)

from django import forms
from django.core.exceptions import ValidationError
from .validators import validate_image_extension
from .models import Persona

class RegistroPersonaForm(forms.Form):
  
    nombre_completo = forms.CharField(label='Nombre Completo', max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control col-6', # Clase de Bootstrap
            'placeholder': 'Ej: Juan Pérez',
        })
    )
    username = forms.CharField(label='Nombre de Usuario', max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control col-6', # Clase de Bootstrap
            'placeholder': 'Ej: juanperez',
        })
    )

        # Campo para la contraseña (input oculto)
    password = forms.CharField(
        label='Contraseña',
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mínimo 8 caracteres',
        })
    )

        # Campo para confirmar la contraseña
    password_confirmacion = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
        })
    )

    identificacion = forms.CharField(
        label='Número de Identificación',
        max_length=10,
        min_length=8,
        widget=forms.TextInput(attrs={
            'class': 'form-control col-6',
            'placeholder': 'Ingrese su cedula o pasaporte',
        })
    )
    
    # Campo para el correo electrónico (requiere formato válido)
    email = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ejemplo@correo.com',
        })
    )

    telefono = forms.CharField(
        label='Número de Teléfono',
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Opcional',
        })
    )

    direccion = forms.CharField(
        label='Dirección',
        max_length=200,
        required=False, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Calle Falsa 123',
        })
    )

    especialidad = forms.CharField(
        label='Especialidad',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control col-6',
            'placeholder': 'Ej: Medicina General',
        })
    )

    # Validación adicional: Asegurar que las contraseñas coincidan
    def clean_password_confirmacion(self):
        # Obtiene los datos limpios de los campos
        password = self.cleaned_data.get('password')
        password_confirmacion = self.cleaned_data.get('password_confirmacion')

        if password and password_confirmacion and password != password_confirmacion:
            # Lanza un error si no coinciden
            raise ValidationError("Las contraseñas no coinciden.")
            
        return password_confirmacion
    
class LoginForm(forms.Form):
    username = forms.CharField(
        label='Nombre de Usuario',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su nombre de usuario',
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña',
        })
    )

class RegistroClienteForm(forms.Form):
  
    nombre_completo = forms.CharField(label='Nombre Completo', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control col-6', 'placeholder': 'Ej: Juan Pérez', }))
    identificacion = forms.CharField(label='Número de Identificación',max_length=10,min_length=8, widget=forms.TextInput(attrs={'class': 'form-control col-6','placeholder': 'Ingrese su cedula o pasaporte',}))    
    email = forms.EmailField(label='Correo Electrónico',widget=forms.EmailInput(attrs={    'class': 'form-control',    'placeholder': 'ejemplo@correo.com' }))
    telefono = forms.CharField(label='Número de Teléfono',max_length=15,required=False, widget=forms.TextInput(attrs={ 'class': 'form-control', 'placeholder': 'Opcional',}))
    direccion = forms.CharField( label='Dirección', max_length=200, required=False,  widget=forms.TextInput(attrs={ 'class': 'form-control', 'placeholder': 'Ej: Calle Falsa 123'}) )

class RegistroMascotaForm(forms.Form):
    archivo = forms.FileField(
        label='Foto de la Mascota',
        help_text='Máx. 2.5 MB',
        required=False,
        validators=[validate_image_extension]
    )

    nombre = forms.CharField(
        label='Nombre de la Mascota',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Firulais',
        })
    )
    especie = forms.CharField(
        label='Especie',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Perro, Gato, etc.',
        })
    )
    raza = forms.CharField(
        label='Raza',
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Opcional',
        })
    )
    edad = forms.IntegerField(
        label='Edad (en años)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 3',
        })
    )


    

class RegistroDoctorForm(forms.Form):
    nombre_completo = forms.CharField(label='Nombre Completo', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control col-6', 'placeholder': 'Ej: Juan Pérez', }))
    identificacion = forms.CharField(label='Número de Identificación',max_length=10,min_length=8, widget=forms.TextInput(attrs={'class': 'form-control col-6','placeholder': 'Ingrese su cedula o pasaporte',}))    
    email = forms.EmailField(label='Correo Electrónico',widget=forms.EmailInput(attrs={    'class': 'form-control',    'placeholder': 'ejemplo@correo.com' }))
    telefono = forms.CharField(label='Número de Teléfono',max_length=15,required=False, widget=forms.TextInput(attrs={ 'class': 'form-control', 'placeholder': 'Opcional',}))
    direccion = forms.CharField( label='Dirección', max_length=200, required=False,  widget=forms.TextInput(attrs={ 'class': 'form-control', 'placeholder': 'Ej: Calle Falsa 123'}) )
    especialidad = forms.CharField(label='Especialidad', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control col-6', 'placeholder': 'Ej: Cardiología', }))

class PersonaForm(forms.Form):
    persona = forms.ModelChoiceField(
        label='Seleccione una Persona',
        queryset=Persona.objects.all(),
        widget=forms.Select(attrs={
            'class': 'select2 col-12',
        })
    )


class PersonaDoctorForm(forms.Form):
    persona = forms.ModelChoiceField(
        label='Seleccione una Persona',
        queryset=Persona.objects.filter(usuario__isnull=False),
        widget=forms.Select(attrs={
            'class': 'select2 col-12',
        })
    )
    especialidad = forms.CharField(
        label='Especialidad',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control col-6',
            'placeholder': 'Ej: Cardiología',
        })
    )

class ReconocimientoForm(forms.Form):
    archivo = forms.ImageField(
            label='Subir imagen',
            required=False,  # Hazlo opcional si lo deseas
            widget=forms.FileInput(attrs={
                'class': 'form-control-file col-12',
            })
        )
