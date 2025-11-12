# blog/urls.py

from django.urls import path

from login.views import clients, home, panel, mascota, logout, config, inference

urlpatterns = [
    path('', home.view, name='inicio'),
    path('home', home.view, name='inicio'),
    path('panel/', panel.view, name='panel'),
    path('logout/', logout.view, name='logout'),
    path('clientes/', clients.view, name='clientes'),
    path('mascotas/', mascota.view, name='mascota'),
    path('config/', config.view, name='config'),
    path('video_feed', inference.video_feed, name='video_feed'),  # Inferencia en tiempo real


    
]