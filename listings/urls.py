from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.landlord_upload, name='landlord_upload'),  # ← new
]