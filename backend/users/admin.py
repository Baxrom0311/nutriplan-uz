from django.contrib import admin
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.token_blacklist.admin import OutstandingTokenAdmin

# Unregister SimpleJWT token models because their default admin classes
# are incompatible with Django 4.0+ and cause AttributeError: 'super' object has no attribute 'dicts'
admin.site.unregister(OutstandingToken)
admin.site.unregister(BlacklistedToken)

# Register CustomUser and UserProfile
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile

admin.site.register(CustomUser, UserAdmin)
admin.site.register(UserProfile)
