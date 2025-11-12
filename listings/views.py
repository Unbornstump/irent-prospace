from django.shortcuts import render, redirect
from .models import Property
from .forms import PropertyForm, PropertyImageForm
from .models import Property, PropertyImage


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


def landlord_upload(request):
    if request.method == 'POST':
        p_form = PropertyForm(request.POST)
        files = request.FILES.getlist('images')   # name="images" from new form
        if p_form.is_valid():
            prop = p_form.save()
            for f in files:
                PropertyImage.objects.create(property=prop, image=f)
            return redirect('home')
    else:
        p_form = PropertyForm()
    return render(request, 'listings/landlord_upload.html', {'form': p_form})

def property_detail(request, pk):
    prop = Property.objects.get(pk=pk)
    return render(request, 'listings/property_detail.html', {'property': prop})

def monitor(request):
    from django.contrib.auth.models import User
    total_props   = Property.objects.count()
    available     = Property.objects.filter(available=True).count()
    total_users   = User.objects.count()
    recent_props  = Property.objects.order_by('-created_at')[:10]
    return render(request, 'listings/monitor.html', {
        'total_props': total_props,
        'available': available,
        'total_users': total_users,
        'recent_props': recent_props,
    })