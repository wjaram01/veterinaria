# blog/views.py

from pyexpat.errors import messages
from django.shortcuts import render
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect
from ..forms import RegistroPersonaForm, LoginForm
from ..models import Persona, Cliente, Doctor
from django.contrib.auth import authenticate, login, get_user_model
from django.db import transaction

@transaction.atomic
def view(request):
    data = {}
    if request.user and request.user.is_authenticated:
        return redirect('/panel')
    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'register':
            try:
                form = RegistroPersonaForm(request.POST)
                User = get_user_model()
                if form.is_valid():
                    if form.cleaned_data['password'] != form.cleaned_data['password_confirmacion']:
                            return JsonResponse({'result': False, 'message': 'Las contraseñas no coinciden'})
                    if not Persona.objects.filter(identificacion=form.cleaned_data['identificacion']).exists():
                        ePersona = Persona(
                            nombre_completo=form.cleaned_data['nombre_completo'],
                            identificacion=form.cleaned_data['identificacion'],
                            email=form.cleaned_data['email'],
                            direccion=form.cleaned_data['direccion'],
                            telefono=form.cleaned_data['telefono']
                        )
                        ePersona.save()
                    else:
                        raise NameError('ya estas registrado.')
                    if not User.objects.filter(username=form.cleaned_data['username']).exists():
                        nuevo_usuario = User(
                            username=form.cleaned_data['username'], 
                            email=form.cleaned_data['email'], 
                            password=form.cleaned_data['password']
                        )
                        nuevo_usuario.set_password(form.cleaned_data['password'])  # Hashear la contraseña
                        nuevo_usuario.save()

                        ePersona.usuario = nuevo_usuario
                        ePersona.save()
                    else:
                        raise NameError('Ya existe un usuario con ese nombre de usuario.')

                    if not Doctor.objects.filter(persona=ePersona).exists():
                        Doctor.objects.create(persona=ePersona, especialidad=form.cleaned_data['especialidad'])

                    return JsonResponse({'result': True, 'message': 'Registro exitoso'})
                else:
                    return JsonResponse({'result': False, 'form': form.errors})
            except Exception as e:
                transaction.set_rollback(True)
                return JsonResponse({'result': False, 'message': str(e)})
            
        elif action == 'login':
            try:
            
                form = LoginForm(request.POST)
                
                if form.is_valid():
                    username = form.cleaned_data.get('username')
                    password = form.cleaned_data.get('password')
                    
                    user = authenticate(request, username=username, password=password)
                    
                    if user is not None:
                        login(request, user)
                        return JsonResponse({'result': True, 'to': '/panel'})

                    else:        
                        return JsonResponse({'result': False, 'message': 'Nombre de usuario o contraseña incorrectos.'})
            except Exception as e:
                return JsonResponse({'result': False, 'message': str(e)})
                        
        

            return render(request, 'login.html', {'form': form})
            
            
            
        return JsonResponse({'result': False, 'message': 'Acción no válida'})
    else:
        action = request.GET.get('action', '')
        
        if action == 'register':
            data['form'] = RegistroPersonaForm()
            data['title'] = 'Página de Registro'
            return render(request, 'home/registro.html', data)
        
        elif action == 'login':
            data['title'] = 'Iniciar Sesión'
            data['form'] = LoginForm()
            data['action'] = 'login'
            return render(request, 'home/login.html', data)
        else:
            data['title'] = 'Página de Inicio'
            return render(request, 'home/inicio.html', data)