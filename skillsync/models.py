from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, full_name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('employer', 'Employer'),
        ('worker',   'Worker'),
    )
    DAYS_CHOICES = [
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'),
        ('Fri', 'Friday'),
        ('Sat', 'Saturday'),
        ('Sun', 'Sunday'),
    ]

    # Core fields
    email       = models.EmailField(unique=True)
    full_name   = models.CharField(max_length=150)
    role        = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    # Professional details
    skills        = models.CharField(max_length=300, blank=True, help_text='Comma-separated skills e.g. Plumbing, Welding')
    hourly_wage   = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text='Hourly rate in KES')
    hours_per_day = models.PositiveIntegerField(null=True, blank=True, help_text='Comfortable working hours per day')
    working_days  = models.CharField(max_length=100, blank=True, help_text='Comma-separated days e.g. Mon,Tue,Wed')

    groups = models.ManyToManyField(
        'auth.Group', blank=True,
        related_name='skillsync_users', verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', blank=True,
        related_name='skillsync_users', verbose_name='user permissions',
    )

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['full_name']
    objects = UserManager()

    def get_skills_list(self):
        return [s.strip() for s in self.skills.split(',') if s.strip()]

    def get_working_days_list(self):
        return [d.strip() for d in self.working_days.split(',') if d.strip()]

    def __str__(self):
        return f"{self.full_name} ({self.role})"
