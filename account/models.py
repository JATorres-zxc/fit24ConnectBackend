from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from datetime import date

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)  # Optional
    contact_number = models.CharField(max_length=15, null=True, blank=True)  # Optional
    messenger_account = models.CharField(max_length=255, blank=True, null=True)
    complete_address = models.TextField(null=True, blank=True)  # Optional
    nationality = models.CharField(max_length=100, null=True, blank=True)  # Optional
    birthdate = models.DateField(null=True, blank=True)  # Optional
    gender = models.CharField(
        max_length=10, 
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        null=True, blank=True  # Optional
    )
    type_of_membership = models.CharField(
        max_length=10,
        choices=[('tier1', 'Tier 1'), ('tier2', 'Tier 2'), ('tier3', 'Tier 3')],
        default='tier1'
    )
    referral_code = models.CharField(max_length=50, blank=True, null=True)
    membership_start_date = models.DateField(null=True, blank=True)
    membership_end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Removed 'full_name' from required fields

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    @property
    def is_membership_active(self):
        """Check if the user's membership is currently active."""
        if self.membership_end_date:
            return self.membership_end_date >= date.today()
        return False