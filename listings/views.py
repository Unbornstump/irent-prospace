from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q

from .models import Property, PropertyImage
from .forms import PropertyForm
from accounts.models import Profile

# Remove old utils import if replaced
# from listings.utils import resize_image  # ❌ remove this

# Correct import for the new image processing function
from listings.image_utils import resize_and_optimize_image

# Optional template helper
from listings.html_utils import build_picture_tag



# -------------------------------------------------------------
# CONTACT PAGE (FINAL VERSION)
# -------------------------------------------------------------
def contact(request):
    """Handles contact form email sending."""
    if request.method == 'POST':
        name    = request.POST.get('name', '').strip()
        email   = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and message:
            subject = f'iRent ProSpace message from {name}'
            body    = f'Name: {name}\nEmail: {email}\n\nMessage:\n{message}'

            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [settings.DEFAULT_FROM_EMAIL])
            messages.success(request, 'Thank you! Your message has been sent.')
            return redirect('contact')

        else:
            messages.error(request, 'Please fill in all fields.')

    return render(request, 'listings/contact.html')


# -------------------------------------------------------------
# HOME + SEARCH (ULTRA STRICT - EXACT MATCHES ONLY)
# -------------------------------------------------------------
def home(request):
    # Check user type
    is_landlord = False
    if request.user.is_authenticated:
        profile, _ = Profile.objects.get_or_create(user=request.user, defaults={'user_type': 'tenant'})
        is_landlord = profile.user_type == 'landlord'

    # Get search parameters
    location = request.GET.get('location', '').strip()
    bedrooms = request.GET.get('bedrooms', '')
    price    = request.GET.get('price', '')
    show_all = request.GET.get('show', '') == 'all'

    # Start with available properties
    qs = Property.objects.filter(available=True)

    # If "show all" button was clicked, show all properties
    if show_all:
        return render(request, 'listings/home.html', {
            'properties': qs.order_by('-created_at'),
            'bedroom_choices': Property.PROPERTY_TYPES,
            'is_landlord': is_landlord,
            'show_all': True,
        })

    # If ALL THREE criteria are NOT provided, show NO results
    if not (location and bedrooms and price):
        return render(request, 'listings/home.html', {
            'properties': Property.objects.none(),
            'bedroom_choices': Property.PROPERTY_TYPES,
            'is_landlord': is_landlord,
            'search_location': location,
            'search_bedrooms': bedrooms,
            'search_price': price,
        })

    # Parse price
    try:
        price_int = int(price)
    except ValueError:
        # Invalid price - show no results
        return render(request, 'listings/home.html', {
            'properties': Property.objects.none(),
            'bedroom_choices': Property.PROPERTY_TYPES,
            'is_landlord': is_landlord,
            'search_location': location,
            'search_bedrooms': bedrooms,
            'search_price': price,
        })

    # ULTRA STRICT FILTERING - ALL CONDITIONS MUST MATCH
    filtered_qs = qs.filter(
        Q(location__iexact=location) |  # Exact location match (case insensitive)
        Q(location__icontains=location),  # Or contains the location
        bedrooms__iexact=bedrooms,  # Exact bedroom type match
        price__lte=price_int,  # Price must be less than or equal to search price
        price__gte=(price_int * 0.8)  # Price must be at least 80% of search price
    )

    # If no matches with strict criteria, return empty
    if not filtered_qs.exists():
        filtered_qs = Property.objects.none()

    return render(request, 'listings/home.html', {
        'properties': filtered_qs.order_by('-created_at'),
        'bedroom_choices': Property.PROPERTY_TYPES,
        'is_landlord': is_landlord,
        'search_location': location,
        'search_bedrooms': bedrooms,
        'search_price': price,
    })


# -------------------------------------------------------------
# LANDLORD UPLOAD
# -------------------------------------------------------------

@login_required
def landlord_upload(request):
    if not Profile.objects.filter(user=request.user, user_type='landlord').exists():
        return redirect('home')

    if request.method == 'POST':
        form = PropertyForm(request.POST)
        files = request.FILES.getlist('images')

        if form.is_valid():
            prop = form.save(commit=False)
            prop.owner_name = request.user.username
            prop.save()

            for f in files:
                processed = resize_and_optimize_image(f)

                # Malware detection
                if "error" in processed:
                    messages.error(request, processed["error"])
                    continue

                # Duplicate detection
                if processed.get("duplicate"):
                    messages.warning(request, "Duplicate image skipped.")
                    continue

                # Save the processed versions
                PropertyImage.objects.create(property=prop, image=processed["desktop"])
                PropertyImage.objects.create(property=prop, image=processed["mobile"])
                PropertyImage.objects.create(property=prop, image=processed["webp"])

                # If file was huge, show warning
                if processed.get("warning"):
                    messages.warning(request, processed["warning"])

            messages.success(request, "Property uploaded successfully!")
            return redirect('home')

    else:
        form = PropertyForm()

    return render(request, 'listings/landlord_upload.html', {'form': form})



# -------------------------------------------------------------
# MONITOR PAGE
# -------------------------------------------------------------
def monitor(request):
    from django.contrib.auth.models import User

    return render(request, 'listings/monitor.html', {
        'total_props': Property.objects.count(),
        'available': Property.objects.filter(available=True).count(),
        'total_users': User.objects.count(),
        'recent_props': Property.objects.order_by('-created_at')[:10],
    })


# -------------------------------------------------------------
# LANDLORD PROPERTY LIST
# -------------------------------------------------------------
@login_required
def my_properties(request):
    if not Profile.objects.filter(user=request.user, user_type='landlord').exists():
        return redirect('home')

    props = Property.objects.filter(owner_name=request.user.username).order_by('-created_at')
    return render(request, 'listings/my_properties.html', {'properties': props})


# -------------------------------------------------------------
# LOGOUT
# -------------------------------------------------------------
def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('home')


# -------------------------------------------------------------
# EDIT PROPERTY
# -------------------------------------------------------------
@login_required
def edit_property(request, pk):
    prop = get_object_or_404(Property, pk=pk, owner_name=request.user.username)

    if request.method == 'POST':
        form = PropertyForm(request.POST, instance=prop)
        files = request.FILES.getlist('images')

        if form.is_valid():
            form.save()

            # Replace images if new ones uploaded
            if files:
                prop.images.all().delete()
                for file in files:
                    PropertyImage.objects.create(property=prop, image=file)

            messages.success(request, 'Listing updated successfully.')
            return redirect('my_properties')

    else:
        form = PropertyForm(instance=prop)

    return render(request, 'listings/edit_property.html', {'form': form, 'prop': prop})


# -------------------------------------------------------------
# DELETE PROPERTY
# -------------------------------------------------------------
@login_required
def delete_property(request, pk):
    prop = get_object_or_404(Property, pk=pk, owner_name=request.user.username)

    if request.method == 'POST':
        prop.delete()
        messages.success(request, 'Listing deleted.')
        return redirect('my_properties')

    return render(request, 'listings/delete_confirm.html', {'prop': prop})


# -------------------------------------------------------------
# STATIC PAGES
# -------------------------------------------------------------
def about(request):
    return render(request, 'listings/about.html')


def property_detail(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    return render(request, 'listings/property_detail.html', {'property': prop})