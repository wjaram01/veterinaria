# blog/views.py

from datetime import datetime
import json
from pyexpat.errors import messages
from django.shortcuts import render
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.shortcuts import redirect
from ..forms import RegistroPersonaForm, LoginForm, RegistroClienteForm, RegistroMascotaForm, RegistroDoctorForm, PersonaDoctorForm
from ..models import Persona, Cliente, Doctor, Mascota
from django.contrib.auth import authenticate, login, get_user_model
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.template import loader
from django.forms.models import model_to_dict
from django.core.paginator import Paginator
from django.db.models import Q

@transaction.atomic
@login_required(login_url="/")
def view(request):
    data = {}
    if request.method == 'POST':
        action = request.POST.get('action', '')
       
        if action == 'adddoctor':
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
                        ePersona = Persona.objects.get(identificacion=form.cleaned_data['identificacion'])
                        ePersona.nombre_completo = form.cleaned_data['nombre_completo']
                        ePersona.email = form.cleaned_data['email']
                        ePersona.direccion = form.cleaned_data['direccion']
                        ePersona.telefono = form.cleaned_data['telefono']
                        ePersona.save()
        
                    if not ePersona.usuario:
                        nuevo_usuario = User(
                            username=form.cleaned_data['username'], 
                            email=form.cleaned_data['email'], 
                            password=form.cleaned_data['password']
                        )
                        nuevo_usuario.set_password(form.cleaned_data['password'])  # Hashear la contraseña
                        nuevo_usuario.save()

                        ePersona.usuario = nuevo_usuario
                        ePersona.save()

                    if not Doctor.objects.filter(persona=ePersona).exists():
                        Doctor.objects.create(persona=ePersona, especialidad=form.cleaned_data['especialidad'])

                    return JsonResponse({'result': True, 'message': 'Registro exitoso'})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'result': False, 'message': form.errors})
            except Exception as e:
                transaction.set_rollback(True)
                return JsonResponse({'result': False, 'message': str(e)})
            

        elif action == 'editdoctor':
            try:
                id = request.POST.get('id', '')
                doctor = Doctor.objects.get(id=id)
                persona = doctor.persona
                form = RegistroPersonaForm(request.POST)
                if form.is_valid():
                    persona.nombre_completo = form.cleaned_data['nombre_completo']
                    persona.identificacion = form.cleaned_data['identificacion']
                    persona.email = form.cleaned_data['email']
                    persona.direccion = form.cleaned_data['direccion']
                    persona.telefono = form.cleaned_data['telefono']
                    persona.save()
                    doctor.especialidad = form.cleaned_data['especialidad']
                    doctor.save()
                    return JsonResponse({'result': True, 'message': 'Doctor actualizado exitosamente'})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'result': False,'form': json.loads(form.errors.as_json())})
            except Exception as e:
                transaction.set_rollback(True)
                return JsonResponse({'result': False, 'message': str(e)})
            

        elif action == 'deldoctor':
            try:
                id = request.POST.get('id', '')
                doctor = Doctor.objects.get(id=id)
                persona = doctor.persona
                doctor.delete()
                return JsonResponse({'result': True, 'message': 'Doctor eliminado exitosamente'})
            except Exception as e:
                transaction.set_rollback(True)
                return JsonResponse({'result': False, 'message': str(e)})
            
        elif action == 'addoctorpersonaexist':
            try:
                form = PersonaDoctorForm(request.POST)
                if form.is_valid():
                    if Doctor.objects.filter(persona_id=form.cleaned_data['persona']).exists():
                        raise NameError('La persona ya esta registrada como un doctor.')

                    Doctor.objects.create(persona=form.cleaned_data['persona'], especialidad=form.cleaned_data['especialidad'])
                    return JsonResponse({'result': True, 'message': 'Registro exitoso'})
                else:
                    return JsonResponse({'result': False, 'message': form.errors})
            except Exception as e:
                transaction.set_rollback(True)
                return JsonResponse({'result': False, 'message': str(e)})
            

        return JsonResponse({'result': False, 'message': 'Acción no válida'})
    else:
        action = request.GET.get('action', '')
        if action:
            if action == 'adddoctor':
                try:
                    form = RegistroPersonaForm()
                    data['form'] = form
                    data['action'] = action
                    template = loader.get_template('formodalbase.html')
                    return JsonResponse({'result': True, 'html': template.render(data, request)})      
                except Exception as e:
                    return JsonResponse({'result': False, 'message': str(e)})
                

            elif action == 'editdoctor':
                try:
                    id = request.GET.get('id', '')
                    data['id'] = id
                    doctor = Doctor.objects.get(id=id)
                    form = RegistroPersonaForm(initial=model_to_dict(doctor.persona))
                    form.fields['especialidad'].initial = doctor.especialidad
                    data['form'] = form
                    data['action'] = action
                    template = loader.get_template('formodalbase.html')
                    return JsonResponse({'result': True, 'html': template.render(data, request)})      
                except Exception as e:
                    return JsonResponse({'result': False, 'message': str(e)})
                
            elif action == 'addoctorpersonaexist':
                try:
                    data['id'] = request.GET.get('id', '')
                    form = PersonaDoctorForm()
                    data['form'] = form
                    data['action'] = action
                    template = loader.get_template('formodalbase.html')
                    return JsonResponse({'result': True, 'html': template.render(data, request)})      
                except Exception as e:
                    return JsonResponse({'result': False, 'message': str(e)})
                
                
            elif action == 'doctores':
                try:
                    data['title'] = 'Listado de doctores'
                    search = request.GET.get('search', '')
                    filtro = Q()
                    if search:
                        filtro &= Q(persona__nombre_completo__icontains=search)
                    listado = Doctor.objects.filter(filtro)
                    paginator = Paginator(listado, 10)
                    page_number = request.GET.get('page')
                    page_obj = paginator.get_page(page_number)
                    data['page_obj'] = page_obj
                    data['back'] = '/config'
                    return render(request, 'config/doctor.html', data)
                except Exception as e:
                    pass
                
            return redirect('/')
        else:
            data['title'] = 'Administración del sistema'
            data['modulos'] = [
                {'title': 'Gestión de doctores', 'descripcion': 'En esta seccion encontrara el listado de doctores', 'url': '/config?action=doctores', 'img': 'images/persons.png'},
            ]
            data['back'] = '/panel'
            return render(request, 'config/view.html', data)