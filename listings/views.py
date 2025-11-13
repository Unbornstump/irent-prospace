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
    # 1. safe landlord check: create temp profile only if missing, then delete if tenant-default
    is_landlord = False
    if request.user.is_authenticated:
        profile, created = Profile.objects.get_or_create(user=request.user, defaults={'user_type': 'tenant'})
        is_landlord = profile.user_type == 'landlord'
        if created and not is_landlord:   # we just made a temp tenant profile → delete it
            profile.delete()

    # 2. normal search logic
    qs = Property.objects.filter(available=True).order_by('-created_at')
    location   = request.GET.get('location', '')
    bedrooms   = request.GET.get('bedrooms', '')
    price_range= request.GET.get('price_range', '')

    if location:
        qs = qs.filter(location__icontains=location)
    if bedrooms:
        qs = qs.filter(bedrooms=bedrooms)

    if price_range == '1-5k':
        qs = qs.filter(price__gte=1000, price__lte=5000)
    elif price_range == '5-10k':
        qs = qs.filter(price__gte=5001, price__lte=10000)
    elif price_range == '10-20k':
        qs = qs.filter(price__gte=10001, price__lte=20000)
    elif price_range == '20k+':
        qs = qs.filter(price__gte=20001)

    # 3. context
    context = {
        'properties': qs,
        'bedroom_choices': Property.PROPERTY_TYPES,
        'is_landlord': is_landlord,
    }
    return render(request, 'listings/home.html', context)

@login_required
def landlord_upload(request):
    # if user is not a landlord, boot them out
    if not Profile.objects.filter(user=request.user, user_type='landlord').exists():
        return redirect('home')
    
    if request.method == 'POST':
        p_form = PropertyForm(request.POST)
        files = request.FILES.getlist('images')
        if p_form.is_valid():
            prop = p_form.save(commit=False)
            prop.owner_name = request.user.username   # force correct owner
            prop.save()
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