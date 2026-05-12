from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.base_user import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class UserProfile(models.Model):
    GENDER_CHOICES = (
        ('male', _('Erkak')),
        ('female', _('Ayol')),
    )
    
    ACTIVITY_CHOICES = (
        ('sedentary', _('Kam harakatli')),
        ('lightly_active', _('Biroz faol')),
        ('moderately_active', _("O'rtacha faol")),
        ('very_active', _('Juda faol')),
        ('extra_active', _('Nihoyatda faol')),
    )
    
    GOAL_CHOICES = (
        ('lose_weight', _("Vazn yo'qotish")),
        ('maintain_weight', _('Vaznni saqlash')),
        ('gain_weight', _('Vazn olish')),
    )

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    
    # Jismoniy ko'rsatkichlar
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    height_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Maqsad va faollik
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_CHOICES, null=True, blank=True)
    goal = models.CharField(max_length=20, choices=GOAL_CHOICES, null=True, blank=True)
    
    # Hisoblangan qiymatlar (cache)
    bmr = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    tdee = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    daily_calorie_goal = models.IntegerField(null=True, blank=True)
    
    # Makronutrient maqsadlari (gramm)
    protein_goal_g = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    carbs_goal_g = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    fat_goal_g = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    # Qo'shimcha
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} Profile"
        
    def save(self, *args, **kwargs):
        from .calculators import recalculate_user_nutrition
        recalculate_user_nutrition(self)
        super().save(*args, **kwargs)
