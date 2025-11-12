from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    USER_TYPE = (
        ('tenant',   'I am a Tenant'),
        ('landlord', 'I am a Landlord'),
    )
    user_type = forms.ChoiceField(
        choices=USER_TYPE,
        widget=forms.RadioSelect,
        required=True,
        label='I am a'
    )

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')