from django.contrib import admin
from .models import Property, PropertyImage

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'price', 'bedrooms', 'available', 'created_at')
    list_filter = ('available', 'bedrooms', 'created_at')
    search_fields = ('title', 'location', 'owner_name')
    inlines = [PropertyImageInline]