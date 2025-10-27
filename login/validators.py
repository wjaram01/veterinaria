# myapp/validators.py

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_image_extension(value):
    # La propiedad content_type se lee del objeto UploadedFile
    content_type = value.content_type
    
    # 🌟 Definir los tipos MIME permitidos
    valid_mimetypes = [
        'image/jpeg',   # JPG y JPEG
        'image/png'     # PNG
    ]

    if content_type not in valid_mimetypes:
        raise ValidationError(
            _('Tipo de archivo no soportado. Por favor, sube un archivo JPG, JPEG o PNG.'),
            code='invalid_image_type'
        )