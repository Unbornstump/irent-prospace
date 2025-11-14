from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from accounts.models import Profile
from listings.models import Property
from django.contrib import messages 
from .forms import SignUpForm
 # Add this for error messages

# --- SIGNUP VIEW (unchanged) ---
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user_type = form.cleaned_data.get('user_type')

            # Create profile for landlords
            if user_type == 'landlord':
                Profile.objects.create(user=user, user_type='landlord')

            # Log the user in
            login(request, user)

            # For landlords: show loading banner in signup.html
            if user_type == 'landlord':
                return render(request, 'registration/signup.html', {'created': True})

            # Tenants: go to homepage
            return redirect('home')

        return render(request, 'registration/signup.html', {'form': form})

    form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

# --- LOGIN VIEW (replace your old one with this) ---
def user_login(request):
    if request.method == 'POST':
        selected_user_type = request.POST.get('user_type', 'tenant')
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            try:
                profile = Profile.objects.get(user=user)
            except Profile.DoesNotExist:
                profile = None

            if profile and profile.user_type != selected_user_type:
                messages.error(
                    request, 
                    f"You selected '{selected_user_type.capitalize()}' but your account is registered as '{profile.user_type.capitalize()}'. Please select the correct user type."
                )
                return render(request, 'registration/login.html', {'form': form})

            login(request, user)

            if selected_user_type == 'landlord':
                has_props = Property.objects.filter(owner_name=user.username).exists()
                if has_props:
                    return redirect('my_properties')
                else:
                    return redirect('landlord_upload')

            return redirect('home')

    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})
