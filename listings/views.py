from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from .models import Property
from .forms import PropertyForm, PropertyImageForm
from .models import Property, PropertyImage
from django.contrib.auth.decorators import login_required
from accounts.models import Profile
from django.contrib.auth import logout
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from listings.utils import resize_image
from django.db.models import Q

def contact(request):
    if request.method == 'POST':
        name    = request.POST.get('name', '').strip()
        email   = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()
        if name and email and message:
            # send email to yourself
            subject = f'iRent ProSpace message from {name}'
            body    = f'Name: {name}\nEmail: {email}\n\nMessage:\n{message}'
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [settings.DEFAULT_FROM_EMAIL])
            messages.success(request, 'Thank you! Your message has been sent.')
            return redirect('contact')   # PRG pattern
        else:
            messages.error(request, 'Please fill in all fields.')
    return render(request, 'listings/contact.html')


def home(request):
    # 1. landlord flag
    is_landlord = False
    if request.user.is_authenticated:
        prof, _ = Profile.objects.get_or_create(user=request.user, defaults={'user_type': 'tenant'})
        is_landlord = prof.user_type == 'landlord'

    # 2. base queryset
    qs = Property.objects.filter(available=True)

    # 3. mandatory filters
    location = request.GET.get('location', '').strip()
    bedrooms = request.GET.get('bedrooms', '')
    price    = request.GET.get('price', '')          # raw number

    if not (location and bedrooms and price):
        # empty or partial search -> show all
        return render(request, 'listings/home.html', {
            'properties': qs.order_by('-created_at'),
            'bedroom_choices': Property.PROPERTY_TYPES,
            'is_landlord': is_landlord,
        })

    # 4. exact match  (location + bedrooms + price-band)
    try:
        price_int = int(price)
    except ValueError:
        price_int = 0
    band_Q = Q()
    if 1000 <= price_int <= 5000:   band_Q = Q(price__gte=1000, price__lte=5000)
    elif 5001 <= price_int <= 10000:  band_Q = Q(price__gte=5001, price__lte=10000)
    elif 10001 <= price_int <= 20000: band_Q = Q(price__gte=10001, price__lte=20000)
    elif price_int >= 20001:          band_Q = Q(price__gte=20001)

    exact = qs.filter(
        Q(location__icontains=location) &
        Q(bedrooms=bedrooms) &
        band_Q
    )

    # 5. near-match (same location + bedrooms, any price)
    near = qs.filter(
        Q(location__icontains=location) &
        Q(bedrooms=bedrooms)
    ).exclude(pk__in=exact) if exact.exists() else qs.filter(
        Q(location__icontains=location) &
        Q(bedrooms=bedrooms)
    )

    # 6. location-only
    location_only = qs.filter(
        location__icontains=location
    ).exclude(pk__in=exact).exclude(pk__in=near) if exact.exists() or near.exists() else qs.filter(
        location__icontains=location
    )

    # 7. decide what to show
    if exact.exists():
        show_qs = exact
        mode = 'exact'
    elif near.exists():
        show_qs = near
        mode = 'near'
    elif location_only.exists():
        show_qs = location_only
        mode = 'location'
    else:
        show_qs = Property.objects.none()
        mode = 'none'

    return render(request, 'listings/home.html', {
        'properties': show_qs.order_by('-created_at'),
        'bedroom_choices': Property.PROPERTY_TYPES,
        'is_landlord': is_landlord,
        'mode': mode,               # template uses this to print helper text
        'search_location': location,
        'search_bedrooms': bedrooms,
        'search_price': price,
    })

@login_required
def landlord_upload(request):
    if not Profile.objects.filter(user=request.user, user_type='landlord').exists():
        return redirect('home')
    
    if request.method == 'POST':
        p_form = PropertyForm(request.POST)
        files = request.FILES.getlist('images')
        if p_form.is_valid():
            prop = p_form.save(commit=False)
            prop.owner_name = request.user.username
            prop.save()
            for f in files:
                resized = resize_image(f)
                PropertyImage.objects.create(property=prop, image=resized)
            return redirect('home')
    else:
        p_form = PropertyForm()
    return render(request, 'listings/landlord_upload.html', {'form': p_form})

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

@login_required
def my_properties(request):
    if not Profile.objects.filter(user=request.user, user_type='landlord').exists():
        return redirect('home')
    props = Property.objects.filter(owner_name=request.user.username).order_by('-created_at')
    return render(request, 'listings/my_properties.html', {'properties': props})

def contact(request):
    if request.method == 'POST':
        name    = request.POST.get('name', '').strip()
        email   = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()
        if name and email and message:
            # send email to yourself
            subject = f'iRent ProSpace message from {name}'
            body    = f'Name: {name}\nEmail: {email}\n\nMessage:\n{message}'
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [settings.DEFAULT_FROM_EMAIL])
            messages.success(request, 'Thank you! Your message has been sent.')
            return redirect('contact')   # PRG pattern
        else:
            messages.error(request, 'Please fill in all fields.')
    return render(request, 'listings/contact.html')

def contact(request):
    if request.method == 'POST':
        name    = request.POST.get('name', '').strip()
        email   = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()
        if name and email and message:
            # send email to yourself
            subject = f'iRent ProSpace message from {name}'
            body    = f'Name: {name}\nEmail: {email}\n\nMessage:\n{message}'
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [settings.DEFAULT_FROM_EMAIL])
            messages.success(request, 'Thank you! Your message has been sent.')
            return redirect('contact')   # PRG pattern
        else:
            messages.error(request, 'Please fill in all fields.')
    return render(request, 'listings/contact.html')



def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def edit_property(request, pk):
    prop = get_object_or_404(Property, pk=pk, owner_name=request.user.username)  # owner only
    if request.method == 'POST':
        form = PropertyForm(request.POST, instance=prop)
        files = request.FILES.getlist('images')
        if form.is_valid():
            form.save()
            # replace images if new ones uploaded
            if files:
                prop.images.all().delete()
                for f in files:
                    PropertyImage.objects.create(property=prop, image=f)
            messages.success(request, 'Listing updated successfully.')
            return redirect('my_properties')
    else:
        form = PropertyForm(instance=prop)
    return render(request, 'listings/edit_property.html', {'form': form, 'prop': prop})

@login_required
def delete_property(request, pk):
    prop = get_object_or_404(Property, pk=pk, owner_name=request.user.username)
    if request.method == 'POST':
        prop.delete()
        messages.success(request, 'Listing deleted.')
        return redirect('my_properties')
    return render(request, 'listings/delete_confirm.html', {'prop': prop})

def about(request):
    return render(request, 'listings/about.html')

def contact(request):
    return render(request, 'listings/contact.html')

def property_detail(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    return render(request, 'listings/property_detail.html', {'property': prop})