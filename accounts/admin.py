from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import Profile

# Inline admin to show Profile when editing a User
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    readonly_fields = ('profile_image_tag',)

    def profile_image_tag(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 50%;" />',
                obj.image.url
            )
        return "-"
    profile_image_tag.short_description = 'Profile Picture'

# Extend default User admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Separate Profile admin
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'user_type', 'is_verified', 'profile_image_tag')
    search_fields = ('user__username', 'user__email', 'phone')
    readonly_fields = ('profile_image_tag',)

    def profile_image_tag(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 50%;" />',
                obj.image.url
            )
        return "-"
    profile_image_tag.short_description = 'Profile Picture'
