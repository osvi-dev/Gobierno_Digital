from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El Email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)
    
    
class User(AbstractUser):
    # Quitamos el campo username de nuestro modelo de usuario
    username = None
    phone  = models.CharField(max_length=15, blank=True, verbose_name=_("Phone Number"))
    email = models.EmailField(unique=True, verbose_name=_("Email Address"), max_length=255,error_messages={"unique":"Error el correo ya existe"})
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name=_("Date Joined"))
    
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = UserManager()
    