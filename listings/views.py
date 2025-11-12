from django.shortcuts import render
from .models import Property

def home(request):
    qs = Property.objects.filter(available=True).order_by('-created_at')
    location = request.GET.get('location', '')
    bedrooms = request.GET.get('bedrooms', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    if location:
        qs = qs.filter(location__icontains=location)
    if bedrooms:
        qs = qs.filter(bedrooms=bedrooms)
    if min_price:
        qs = qs.filter(price__gte=min_price)
    if max_price:
        qs = qs.filter(price__lte=max_price)

    context = {
        'properties': qs,
        'bedroom_choices': Property.PROPERTY_TYPES,
    }
    return render(request, 'listings/home.html', context)