# blog/views.py

from datetime import datetime
from pyexpat.errors import messages
from django.shortcuts import render
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.shortcuts import redirect
from ..forms import RegistroPersonaForm, LoginForm, RegistroClienteForm, RegistroMascotaForm, ReconocimientoForm
from ..models import Persona, Cliente, Doctor, Mascota
from django.contrib.auth import authenticate, login, get_user_model
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.template import loader
from django.forms.models import model_to_dict
from django.core.paginator import Paginator
from django.db.models import Q
from veterinaria.commonviews import add_data_to_context
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
    
        if action == 'editmascota':
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
            
        elif action == 'testmodel':
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
                        'prediccion': class_name,
                        'confianza': f'{confidence_score * 100:.2f}%',
                        'imagen': f"data:{mime_type};base64,{cadena_base64}"
                    }
                    return JsonResponse({'result': True, 'message': 'Mascota editada exitosamente', 'data': result })
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'result': False, 'message': form.errors})
            except Exception as e:
                import traceback
                traceback.print_exc()
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
            
            
        return JsonResponse({'result': False, 'message': 'Acción no válida'})
    else:
        action = request.GET.get('action', '')
        if action:    
            if action == 'editmascota':
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
                
            elif action == 'testmodel':
                data['title'] = 'Reconocimiento de enfermedades'
                data['form'] = ReconocimientoForm()
                data['action'] = 'testmodel'
                return render(request, 'mascota/recon.html', data)
                
                
            return redirect('/')
        else:
            data['title'] = 'Mascotas de Clientes'
            filtro = Q()
            s = request.GET.get('search', '')
            if s:
                filtro |= Q(persona__nombre_completo__icontains=s)
                filtro |= Q(persona__identificacion__icontains=s)
                filtro |= Q(persona__email__icontains=s)
            listado = Mascota.objects.filter(filtro).order_by('-id')
            paginator = Paginator(listado, 10)
    
            page_number = request.GET.get('page')
            
            page_obj = paginator.get_page(page_number)
            data['page_obj'] = page_obj
            return render(request, 'mascota/view.html', data)