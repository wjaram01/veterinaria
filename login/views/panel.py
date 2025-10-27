# blog/views.py

from pyexpat.errors import messages
from django.shortcuts import render
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect
from ..forms import RegistroPersonaForm, LoginForm
from ..models import Persona, Cliente
from django.contrib.auth import authenticate, login, get_user_model
from django.db import transaction
from django.contrib.auth.decorators import login_required
from veterinaria.commonviews import add_data_to_context

@transaction.atomic
@login_required(login_url="/")
def view(request):
    data = add_data_to_context(request, {})
    data['title'] = 'Página de Inicio'
    data['modulos'] = get_modulos(data)
    return render(request, 'panel/view.html', data)
        

def get_modulos(data):
    persona = data['persona']
    modulos = []
    if  data['user'].is_superuser or persona.es_doctor():
        modulos.append({'title': 'Gestión de Clientes', 'descripcion': 'En esta seccion encontrara el listado de clientes', 'url': '/clientes', 'img': 'images/persons.png'})
        modulos.append({'title': 'Gestión de Mascotas', 'descripcion': 'En esta seccion encontrara el listado de mascotas de los clientes', 'url': '/mascotas', 'img': 'images/dog.png'})

    if data['user'].is_superuser:
        modulos.append({'title': 'Administracion del sistema', 'descripcion': 'En esta seccion administras las configuraciones del sistema', 'url': '/config', 'img': 'images/settings.png'})
    modulos.append({'title': 'Reconocimiento', 'descripcion': 'En esta seccion se encentra la funcion de reconocimiento de enfermedades de la piel.', 'url': '/mascotas?action=testmodel', 'img': 'images/recon.jpg'})
    return modulos
