from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignUpForm
from .models import Profile

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