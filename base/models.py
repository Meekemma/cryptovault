from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.conf import settings


# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        """
        Creates, saves, and returns a User with the given email, first name, last name, and password.
        """
        if not email:
            raise ValueError('User must have an email address')
        if not first_name:
            raise ValueError('First name is required')
        if not last_name:
            raise ValueError('Last name is required')

        email =self.normalize_email(email).lower()
        user = self.model(email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None):
        """
        Creates, saves, and returns a superuser with the given email, first name, last name, and password.
        """
        user = self.create_user(email, first_name, last_name, password)
        user.is_superuser = True
        user.is_staff = True
        user.is_verified = True
        user.save(using=self._db)
        return user
    
    
    

AUTH_PROVIDERS = {'email': 'email', 'google': 'google'}

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    groups = models.ManyToManyField(Group, blank=True)
    auth_provider = models.CharField(max_length=50, default=AUTH_PROVIDERS.get('email'))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super(User, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
        ]






GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Others', 'Others'),
)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True, null=True, blank=True)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, null=True)
    profile_picture = models.ImageField(upload_to='images/profile_images', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])
    phone_number = models.CharField(max_length=50, null=True)
    country = models.CharField(max_length=50, null=True)
    referral_code = models.CharField(max_length=10, unique=True, editable=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"User Profile for {self.user.first_name}"

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['-date_created']
        indexes = [
            models.Index(fields=['user']),
        ]

    @property
    def referral_url(self):
        """
        Generates a referral URL for the user.
        """
        base_url = getattr(settings, 'BASE_URL', 'https://www.trexiz.com')
        return f"{base_url}/signup?ref={self.referral_code}"



class  OneTimePassword(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name}-passcode"
    
    def is_valid(self):
        # OTP is valid for 5 minutes
        now = timezone.now()
        return now - self.created_at <= timezone.timedelta(minutes=5)

    



class Subscription(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_subscribed = models.BooleanField(default=True)

    def __str__(self):
        return self.email
    

    