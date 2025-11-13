from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignUpForm
from .models import Profile
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login 
from accounts.models import Profile
from listings.models import Property


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            ut = form.cleaned_data.get('user_type')
            if ut == 'landlord':
                Profile.objects.create(user=user, user_type='landlord')
                login(request, user)
                return redirect('landlord_upload')   # landlords go straight to upload
            # tenants
            login(request, user)
            return redirect('home')                  # tenants go back to homepage
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})



def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # routing logic
            if Profile.objects.filter(user=user, user_type='landlord').exists():
                has_props = Property.objects.filter(owner_name=user.username).exists()
                print("DEBUG: landlord login → has_props =", has_props)
                if has_props:
                    return redirect('my_properties')
                else:
                    return redirect('landlord_upload')

            # tenants → home
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})
    