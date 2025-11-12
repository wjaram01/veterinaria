from django.shortcuts import render
from django.http import StreamingHttpResponse
import torch
from PIL import Image
import cv2
from login.loader import get_model_and_preprocessor
from veterinaria.commonviews import get_predict

# Cargar modelo y preprocesador
model, processor, device = get_model_and_preprocessor()

# Página principal para cargar el video
def home(request):
    return render(request, 'index.html')

# Función de inferencia en tiempo real con video
def video_feed(request):
    return StreamingHttpResponse(generate_video(), content_type='multipart/x-mixed-replace; boundary=frame')

def generate_video():
    cap = cv2.VideoCapture(0)  # Abre la cámara web (0 es la cámara por defecto)
    threshold = 0.70  # Umbral de confianza para mostrar el recuadro (puedes ajustarlo)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convertir el frame a imagen PIL (para procesamiento con el modelo)
        image_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Preprocesar la imagen para ViT
        inputs = processor(images=image_pil, return_tensors='pt')
        inputs = {key: value.to(device) for key, value in inputs.items()}  # Mover al dispositivo (GPU o CPU)

        # Realizar la inferencia
        with torch.no_grad():
            outputs = model(**inputs)

        # Obtener las probabilidades y los logits
        logits = outputs.logits
        probabilities = torch.nn.functional.softmax(logits, dim=-1)  # Calcular la probabilidad de cada clase

        # Obtener la clase predicha y la probabilidad
        predicted_class_idx = torch.argmax(probabilities, dim=-1).item()
        predicted_class_prob = probabilities[0][predicted_class_idx].item()  # Probabilidad de la clase predicha
        
        # Obtener las clases desde la configuración del modelo (usamos model.config)
        class_names = model.config.id2label
        predicted_class_name = class_names[predicted_class_idx]

        # Si la probabilidad es mayor que el umbral, dibujar el recuadro y mostrar la predicción
        if predicted_class_prob > threshold:
            # Dibujar el recuadro alrededor de una ubicación predeterminada
            # Este recuadro no está basado en la localización de un objeto detectado, sino que es estático.
            cv2.rectangle(frame, (10, 50), (300, 100), (0, 255, 0), 2)  # Coordenadas y color del recuadro
            cv2.putText(frame, f'{get_predict(predicted_class_name)}: {predicted_class_prob:.2f}', (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        else:
            cv2.putText(frame, 'Confidence too low', (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # Codificar el frame como imagen JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            break
        frame_bytes = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

    cap.release()

