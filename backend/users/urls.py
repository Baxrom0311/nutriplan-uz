from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView,
    UserProfileView,
    RecalculateNutritionView,
    ChangePasswordView
)

urlpatterns = [
    # Auth URLs
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', TokenObtainPairView.as_view(), name='auth_login'),
    path('refresh/', TokenRefreshView.as_view(), name='auth_refresh'),
    path('password/reset/', ChangePasswordView.as_view(), name='auth_password_reset'),
    
    # Profile URLs
    path('me/', UserProfileView.as_view(), name='user_profile'),
    path('me/calculate/', RecalculateNutritionView.as_view(), name='recalculate_nutrition'),
]
