from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from datetime import date
from django.utils.timezone import now

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
    full_name = models.CharField(max_length=255, null=True, blank=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    messenger_account = models.CharField(max_length=255, blank=True, null=True)
    complete_address = models.TextField(null=True, blank=True)
    nationality = models.CharField(max_length=100, null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10, 
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        null=True, blank=True
    )
    type_of_membership = models.CharField(
        max_length=10,
        choices=[('tier1', 'Tier 1'), ('tier2', 'Tier 2'), ('tier3', 'Tier 3')],
        default='tier1'
    )
    referral_code = models.CharField(max_length=50, blank=True, null=True)
    membership_start_date = models.DateField(null=True, blank=True)
    membership_end_date = models.DateField(null=True, blank=True)
    
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_trainer = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    
    date_joined = models.DateTimeField(default=now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    @property
    def is_membership_active(self):
        """Check if the user's membership is currently active based on dates."""
        today = date.today()

        # If no dates at all → inactive
        if not self.membership_start_date and not self.membership_end_date:
            return False

        # Must have both dates to be active
        if not self.membership_start_date or not self.membership_end_date:
            return False

        # Check date ranges
        return (self.membership_start_date <= today <= self.membership_end_date)

    @property
    def role(self):
        if self.is_admin:
            return "admin"
        elif self.is_trainer:
            return "trainer"
        return "user"

    @property
    def ensure_trainer_profile(self):
        """Ensure that a Trainer profile is created if the user is a trainer."""
        if self.is_trainer and not hasattr(self, 'trainer_profile'):
            Trainer.objects.create(user=self)
        return self.trainer_profile
    
    def save(self, *args, **kwargs):
        """Automatically update is_active based on membership dates."""
        # For non-staff/superusers, update is_active based on membership
        if not self.is_superuser and not self.is_staff:
            if self.membership_start_date and self.membership_end_date:
                self.is_active = self.is_membership_active
            else:
                self.is_active = False
        super().save(*args, **kwargs)

class Trainer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="trainer_profile")
    experience = models.TextField(blank=True, default="")
    contact_no = models.CharField(max_length=15, blank=True, default="")

    def __str__(self):
        return self.user.full_name or self.user.email
