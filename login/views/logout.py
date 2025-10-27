# myapp/views.py

from django.shortcuts import redirect
from django.contrib.auth import logout
from django.urls import reverse
from django.contrib import messages # Opcional: para mostrar un mensaje

def view(request):
    """
    Cierra la sesión del usuario actual y lo redirige a la página principal.
    """
    logout(request)
        
    return redirect('/') 