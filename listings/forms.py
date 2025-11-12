from django import forms
from .models import Property, PropertyImage

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['title', 'description', 'location', 'price', 'bedrooms',
                  'owner_name', 'owner_phone']

class PropertyImageForm(forms.Form):
    images = forms.FileField(required=False)   # plain field, no widget tricks