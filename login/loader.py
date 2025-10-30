# mi_app/ml_model/loader.py
import torch
from transformers import AutoModelForImageClassification, AutoImageProcessor, ViTImageProcessor, ViTForImageClassification
from PIL import Image
import os
import sys

# Obtener el directorio base donde se encuentran los archivos del modelo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Rutas de los archivos
# La carpeta BASE_DIR debe contener: config.json, mofr.safetensors, y la carpeta 'preprocessor'
MODEL_PATH = os.path.join('login', 'resources', 'model')

# Variables globales para el modelo
MODEL = None
PREPROCESSOR = None
# Determinar el dispositivo de cómputo (GPU si está disponible, sino CPU)
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_mofr_model():
    """Carga el modelo y el preprocesador de Hugging Face solo una vez."""
    global MODEL, PREPROCESSOR
    
    # Solo cargar si el modelo aún no ha sido inicializado
    if MODEL is None:
        try:
            print("⏳ Cargando modelo de clasificación de imágenes y preprocesador...")
            
            # 1. Cargar el Preprocesador de Imágenes
            # Esto carga la configuración de normalización, redimensionamiento, etc.
            PREPROCESSOR = ViTImageProcessor.from_pretrained(MODEL_PATH)
            
            # 2. Cargar el Modelo para Clasificación de Imágenes
            # AutoModelForImageClassification es ideal para ViT/clasificación
            MODEL = ViTForImageClassification.from_pretrained(
                MODEL_PATH,
                device_map='auto'
            )
            
            MODEL.eval() # Poner el modelo en modo de evaluación
            print(f"✅ Modelo 'mofr' para Clasificación de Imágenes cargado en: {DEVICE}")
            
        except Exception as e:
            # Captura y reporta el error, útil para depuración en el servidor
            print(f"❌ Error al cargar el modelo de Clasificación: {e}", file=sys.stderr)
            print("Asegúrate de que los archivos 'config.json', 'mofr.safetensors' y la carpeta 'preprocessor' estén en el directorio:", MODEL_PATH, file=sys.stderr)
            MODEL = None
            PREPROCESSOR = None

# Función para ser llamada por las vistas de Django
def get_model_and_preprocessor():
    """Retorna el modelo, el preprocesador y el dispositivo."""
    # Intentar cargar si no se ha hecho (puede ocurrir si no usas AppConfig)
    if MODEL is None:
        load_mofr_model()
    
    return MODEL, PREPROCESSOR, DEVICE

