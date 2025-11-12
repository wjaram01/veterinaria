from flask import Flask, render_template, request, Response
import torch
from transformers import ViTImageProcessor, AutoModelForImageClassification
import cv2
import numpy as np
from PIL import Image

app = Flask(__name__)

# Cargar el modelo y el procesador desde los archivos
model_checkpoint = "google/vit-base-patch16-224"  # Asegúrate de usar el checkpoint correcto
processor = ViTImageProcessor.from_pretrained(model_checkpoint)
model = AutoModelForImageClassification.from_pretrained(model_checkpoint)

# Página principal
@app.route('/')
def home():
    return render_template('index.html')

# Ruta para capturar el video y hacer la inferencia
@app.route('/video_feed')
def video_feed():
    return Response(generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Función para generar el video con inferencia en tiempo real
def generate_video():
    cap = cv2.VideoCapture(0)  # Abre la cámara web (o usa un archivo de video)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convierte el frame de OpenCV (BGR) a PIL (RGB)
        image_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Preprocesar la imagen para el modelo ViT
        inputs = processor(images=image_pil, return_tensors='pt', padding=True)

        # Realizar la inferencia
        with torch.no_grad():
            outputs = model(**inputs)

        # Obtener la clase predicha
        logits = outputs.logits
        predicted_class_idx = torch.argmax(logits, dim=-1).item()
        class_names = processor.config.id2label
        predicted_class_name = class_names[predicted_class_idx]

        # Escribir el texto de la clase predicha en el frame
        cv2.putText(frame, f'Predicted: {predicted_class_name}', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Codificar el frame en formato JPEG y enviarlo al cliente
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            break
        frame_bytes = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

    cap.release()

if __name__ == '__main__':
    app.run(debug=True)
