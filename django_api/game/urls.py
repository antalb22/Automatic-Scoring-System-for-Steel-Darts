from django.urls import path
from . import views

urlpatterns = [
    path('init/', views.init_game),
    path('stop/', views.stop_game),
    path('turnon/', views.turn_on_cameras),
]
