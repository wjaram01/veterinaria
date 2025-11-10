# blog/views.py

from datetime import datetime
from pyexpat.errors import messages
from django.shortcuts import render
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.shortcuts import redirect
from ..forms import RegistroPersonaForm, LoginForm, RegistroClienteForm, RegistroMascotaForm, PersonaForm, ReconocimientoForm
from ..models import Persona, Cliente, Doctor, Mascota, DiagnosticoMascota
from django.contrib.auth import authenticate, login, get_user_model
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.template import loader
from django.forms.models import model_to_dict
from django.core.paginator import Paginator
from django.db.models import Q
from veterinaria.commonviews import add_data_to_context, get_predict
from django.contrib import messages
from ..loader import get_model_and_preprocessor
from PIL import Image
import torch
import torch.nn.functional as F
import base64   
import io 


@transaction.atomic
@login_required(login_url="/")
def view(request):
    data = add_data_to_context(request, {})
    if request.method == 'POST':
        action = request.POST.get('action', '')
       
        if action == 'addcliente':
            try:
                form = RegistroClienteForm(request.POST)
                id = request.POST.get('id', '')
                doctor = Doctor.objects.get(id=id)
                if form.is_valid():
                    if not Persona.objects.filter(identificacion=form.cleaned_data['identificacion']).exists():
                        persona = Persona(
                            nombre_completo=form.cleaned_data['nombre_completo'],
                            identificacion=form.cleaned_data['identificacion'],
                            email=form.cleaned_data['email'],
                            direccion=form.cleaned_data['direccion'],
                            telefono=form.cleaned_data['telefono']
                        )
                        persona.save()
                    else:
                        raise NameError('La persona ya está registrada.')
                    if not Cliente.objects.filter(persona=persona, doctor=doctor).exists():
                        eCliente = Cliente(
                            persona=persona,
                            fecha_registro=datetime.now(),
                            doctor=doctor
                        )
                        eCliente.save()
                        return JsonResponse({'result': True, 'message': 'Cliente agregado exitosamente'})
                    else:
                        transaction.set_rollback(True)
                        return JsonResponse({'result': False, 'message': 'El cliente ya existe.'})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'result': False, 'message': form.errors})
            except Exception as e:
                transaction.set_rollback(True)
                return JsonResponse({'result': False, 'message': str(e)})
            

        elif action == 'editcliente':
            try:
                id = request.POST.get('id', '')
                cliente = Cliente.objects.get(id=id)
                persona = cliente.persona
                form = RegistroClienteForm(request.POST)
                if form.is_valid():
                    persona.nombre_completo = form.cleaned_data['nombre_completo']
                    persona.identificacion = form.cleaned_data['identificacion']
                    persona.email = form.cleaned_data['email']
                    persona.direccion = form.cleaned_data['direccion']
                    persona.telefono = form.cleaned_data['telefono']
                    persona.save()
                    return JsonResponse({'result': True, 'message': 'Cliente actualizado exitosamente'})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'result': False, 'message': form.errors})
            except Exception as e:
                transaction.set_rollback(True)
                return JsonResponse({'result': False, 'message': str(e)})
            

        elif action == 'delcliente':
            try:
                id = request.POST.get('id', '')
                cliente = Cliente.objects.get(id=id)
                persona = cliente.persona
                cliente.delete()
                return JsonResponse({'result': True, 'message': 'Cliente eliminado exitosamente'})
            except Exception as e:
                transaction.set_rollback(True)
                return JsonResponse({'result': False, 'message': str(e)})
            

        elif action == 'addmascota':
            try:
                form = RegistroMascotaForm(request.POST)
                id = request.POST.get('id', '')
                cliente = Cliente.objects.get(id=id)
                if form.is_valid():
                    archivo = None
                    if 'archivo' in request.FILES:
                           archivo = request.FILES['archivo']
                    mascota = Mascota(
                        nombre=form.cleaned_data['nombre'],
                        especie=form.cleaned_data['especie'],
                        raza=form.cleaned_data['raza'],
                        edad=form.cleaned_data['edad'],
                        cliente=cliente,
                        archivo=archivo
                    )
                    mascota.save()
                    return JsonResponse({'result': True, 'message': 'Mascota agregada exitosamente'})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'result': False, 'message': form.errors})
            except Exception as e:
                transaction.set_rollback(True)
                return JsonResponse({'result': False, 'message': str(e)})

        elif action == 'editmascota':
            try:
                form = RegistroMascotaForm(request.POST)
                id = request.POST.get('id', '')
                mascota = Mascota.objects.get(id=id)
                if form.is_valid():
                    archivo = None
                    if 'archivo' in request.FILES:
                           archivo = request.FILES['archivo']
                    mascota.nombre = form.cleaned_data['nombre']
                    mascota.especie = form.cleaned_data['especie']
                    mascota.raza = form.cleaned_data['raza']
                    mascota.edad = form.cleaned_data['edad']
                    mascota.archivo = archivo
                    mascota.save()
                    return JsonResponse({'result': True, 'message': 'Mascota editada exitosamente'})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'result': False, 'message': form.errors})
            except Exception as e:
                transaction.set_rollback(True)
                return JsonResponse({'result': False, 'message': str(e)})
            

        elif action == 'delmascota':
            try:
                id = request.POST.get('id', '')
                mascota = Mascota.objects.get(id=id)
                mascota.delete()
                return JsonResponse({'result': True, 'message': 'Mascota eliminada exitosamente'})
            except Exception as e:
                transaction.set_rollback(True)
                return JsonResponse({'result': False, 'message': str(e)})
            
        elif action == 'addclientexistente':
            try:
                form = PersonaForm(request.POST)
                id = request.POST.get('id', '')
                doctor = Doctor.objects.get(id=id)
                if form.is_valid():
                    if not Cliente.objects.filter(persona=form.cleaned_data['persona'], doctor=doctor).exists():
                        eCliente = Cliente(
                            persona=form.cleaned_data['persona'],
                            fecha_registro=datetime.now(),
                            doctor=doctor
                        )
                        eCliente.save()
                        return JsonResponse({'result': True, 'message': 'Cliente agregado exitosamente'})
                    else:
                        transaction.set_rollback(True)
                        return JsonResponse({'result': False, 'message': 'El cliente ya existe.'})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'result': False, 'message': form.errors})
            except Exception as e:
                transaction.set_rollback(True)
                return JsonResponse({'result': False, 'message': str(e)})
            
        elif action == 'addconsulta':
            try:
                model, preprocessor, device = get_model_and_preprocessor()
                result = None
                image_url = None
                if model is None:
                    raise NameError('Modelo no definido')
                form = ReconocimientoForm(request.POST)
                if form.is_valid():
                    archivo = None
                    if 'archivo' in request.FILES:
                           archivo = request.FILES['archivo']
                    image_file =archivo
                    # Abre el archivo como una imagen PIL
                    if not image_file: raise NameError('No ha enviado una imagen')
                    img = Image.open(image_file).convert('RGB')
                    image_url = image_file.name # Placeholder para el nombre del archivo

                    # Preprocesamiento, Inferencia, y Post-procesamiento
                    inputs = preprocessor(images=img, return_tensors="pt").to(device)
                    
                    with torch.no_grad():
                        outputs = model(**inputs)
                    
                    logits = outputs.logits
                    probabilities = F.softmax(logits, dim=1)
                    predicted_class_idx = torch.argmax(probabilities, dim=1).item()
                    confidence_score = probabilities[0][predicted_class_idx].item()
                    
                    # Obtener el nombre de la clase usando el mapeo del modelo
                    class_name = model.config.id2label[predicted_class_idx]

                    image_file.seek(0) 
                    contenido_binario = image_file.read()
                    cadena_base64 = base64.b64encode(contenido_binario).decode('utf-8')
                    mime_type = "image/png"
                    
                    
                    result = {
                        'prediccion': get_predict(class_name),
                        'confianza': f'{confidence_score * 100:.2f}%',
                        'imagen': f"data:{mime_type};base64,{cadena_base64}"
                    }
                    return JsonResponse({'result': True, 'message': 'Mascota', 'data': result })
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'result': False, 'message': form.errors})
            except Exception as e:
                import traceback
                traceback.print_exc()
                transaction.set_rollback(True)
                return JsonResponse({'result': False, 'message': str(e)})
            
        elif action == 'saveconsulta':
            try:
                id = request.POST.get('id', None)
                form = ReconocimientoForm(request.POST)
                if form.is_valid():
                    archivo = None
                    if 'archivo' in request.FILES:
                           archivo = request.FILES['archivo']
                    if not archivo: raise NameError('Debe subir un archivo')
                    mascota = Mascota.objects.get(pk=int(id))
                    pred = request.POST.get('prediccion', None)
                    diag = DiagnosticoMascota(
                        mascota = mascota,
                        fecha_registro = datetime.now(),
                        nombre = pred,
                        archivo = archivo
                    )
                    diag.save()
                    return JsonResponse({'result': True, 'message': 'Guardado correctamente' })
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'result': False, 'message': form.errors})
            except Exception as e:
                transaction.set_rollback(True)
                return JsonResponse({'result': False, 'message': str(e)})
            
        elif action == 'deldiagnostico':
            try:
                id = request.POST.get('id', '')
                diag = DiagnosticoMascota.objects.get(id=id)
                mascota = diag.mascota.id
                diag.delete()
                return JsonResponse({'result': True, 'message': 'Eliminado exitosamente'})
            except Exception as e:
                transaction.set_rollback(True)
                return JsonResponse({'result': False, 'message': str(e)})
            
            
        return JsonResponse({'result': False, 'message': 'Acción no válida'})
    else:
        action = request.GET.get('action', '')
        if action:
            if action == 'addcliente':
                try:
                    form = RegistroClienteForm()
                    data['id'] = request.GET.get('id', '')
                    data['form'] = form
                    data['action'] = 'addcliente'
                    template = loader.get_template('formodalbase.html')
                    return JsonResponse({'result': True, 'html': template.render(data, request)})      
                except Exception as e:
                    return JsonResponse({'result': False, 'message': str(e)})
                

            elif action == 'editcliente':
                try:
                    id = request.GET.get('id', '')
                    data['id'] = id
                    cliente = Cliente.objects.get(id=id)
                    form = RegistroClienteForm(initial=model_to_dict(cliente.persona))
                    data['form'] = form
                    data['action'] = action
                    template = loader.get_template('formodalbase.html')
                    return JsonResponse({'result': True, 'html': template.render(data, request)})      
                except Exception as e:
                    return JsonResponse({'result': False, 'message': str(e)})
                

            if action == 'addmascota':
                try:
                    id = request.GET.get('id', '')
                    data['id'] = id
                    form = RegistroMascotaForm()
                    data['form'] = form
                    data['action'] = action
                    template = loader.get_template('formodalbase.html')
                    return JsonResponse({'result': True, 'html': template.render(data, request)})      
                except Exception as e:
                    return JsonResponse({'result': False, 'message': str(e)})
                

            elif action == 'editmascota':
                try:
                    id = request.GET.get('id', '')
                    data['id'] = id
                    mascota = Mascota.objects.get(id=id)
                    form = RegistroMascotaForm(initial=model_to_dict(mascota))
                    data['form'] = form
                    data['action'] = action
                    template = loader.get_template('formodalbase.html')
                    return JsonResponse({'result': True, 'html': template.render(data, request)})      
                except Exception as e:
                    return JsonResponse({'result': False, 'message': str(e)})

            elif action == 'addclientexistente':
                try:
                    data['id'] = request.GET.get('id', '')
                    form = PersonaForm()
                    data['form'] = form
                    data['action'] = action
                    template = loader.get_template('formodalbase.html')
                    return JsonResponse({'result': True, 'html': template.render(data, request)})      
                except Exception as e:
                    return JsonResponse({'result': False, 'message': str(e)})
                
            elif action == 'mismascotas':
                try:
                    id = request.GET.get('id', '')
                    data['id'] = id
                    data['cliente'] = cliente = Cliente.objects.get(id=id)

                    listado = cliente.mascota_set.all()
                    paginator = Paginator(listado, 10)
                    page_number = request.GET.get('page')
                    page_obj = paginator.get_page(page_number)
                    data['page_obj'] = page_obj
                    data['back'] = '/clientes'
                    return render(request, 'client/mascota.html', data)
                except Exception as e:
                    pass

            elif action == 'addconsulta':
                try:
                    data['id'] = request.GET.get('id', '')
                    form = ReconocimientoForm()
                    data['form'] = form
                    data['action'] = action
                    template = loader.get_template('client/modal/formdiagnostico.html')
                    return JsonResponse({'result': True, 'html': template.render(data, request)})      
                except Exception as e:
                    return JsonResponse({'result': False, 'message': str(e)})

            elif action == 'historialmascota':
                try:
                    id = request.GET.get('id', '')
                    data['id'] = id
                    data['mascota'] = mascota = Mascota.objects.get(id=id)

                    listado = DiagnosticoMascota.objects.filter(mascota=mascota)
                    paginator = Paginator(listado, 10)
                    page_number = request.GET.get('page')
                    page_obj = paginator.get_page(page_number)
                    data['page_obj'] = page_obj
                    data['back'] = f'/clientes?action=mismascotas&id={mascota.cliente.id}'
                    return render(request, 'client/diagnostico.html', data)
                except Exception as e:
                    pass
                
            return redirect('/')
        else:
            data['title'] = 'Clientes'
            filtro = Q()
            s = request.GET.get('search', '')
            if s:
                filtro |= Q(persona__nombre_completo__icontains=s)
                filtro |= Q(persona__identificacion__icontains=s)
                filtro |= Q(persona__email__icontains=s)

            if data.get('doctor'):
                filtro &= Q(doctor=data['doctor'])
            elif request.user.is_superuser:
                pass
            else:
                messages.warning(request, 'Debes ser un doctor para ver los clientes.')
                return redirect('/')
            listado = Cliente.objects.filter(filtro).order_by('-id')
            paginator = Paginator(listado, 10)
    
            page_number = request.GET.get('page')
            
            page_obj = paginator.get_page(page_number)
            data['page_obj'] = page_obj
            data['back'] = '/panel'
            return render(request, 'client/view.html', data)