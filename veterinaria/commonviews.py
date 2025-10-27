from login.models import Persona, Doctor

def add_data_to_context(request, data):
    data = {}
    """
    Agrega datos comunes al contexto de las vistas.
    """

    data['user'] = request.user
    data['persona'] = persona = Persona.objects.filter(usuario=request.user).first()
    if persona: 
        data['doctor'] = doctor = Doctor.objects.filter(persona=persona).first()
    return data