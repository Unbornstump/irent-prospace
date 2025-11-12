from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.landlord_upload, name='landlord_upload'),
    path('property/<int:pk>/', views.property_detail, name='property_detail'),
    path('myadmin007/', views.monitor, name='monitor'),
    path('my-properties/', views.my_properties, name='my_properties'),
]