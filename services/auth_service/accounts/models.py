from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
   
    USER_TYPE_CHOICES = [
        ('PETITIONER', 'Petitioner'),
        ('RESPONDENT', 'Respondent'),
        ('PROSECUTION', 'Prosecution'),
        ('DEFENSE', 'Defense'),
        ('MEDIATOR', 'Mediator'),
        ('JUDGE', 'Judge'),  
        ('COURT_STAFF', 'Court Staff'), 
        ('OBSERVER', 'Observer'),  
    ]
    
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='OBSERVER',
        help_text="Type of user in the court hearing system"
    )
    
    # Additional fields for legal platform
    bar_number = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        help_text="Bar registration number for lawyers/attorneys"
    )
    license_number = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        help_text="Professional license number"
    )
    organization = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        help_text="Law firm, court, or organization name"
    )
    phone_number = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        help_text="Contact phone number"
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether the user's credentials have been verified"
    )
    verification_date = models.DateTimeField(
        blank=True, 
        null=True,
        help_text="Date when user was verified"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

    def is_legal_professional(self):
        """Check if user is a legal professional (lawyer, prosecutor, etc.)"""
        return self.user_type in ['PROSECUTION', 'DEFENSE', 'MEDIATOR', 'JUDGE']
    
    def is_case_participant(self):
        """Check if user is a direct participant in cases"""
        return self.user_type in ['PETITIONER', 'RESPONDENT', 'PROSECUTION', 'DEFENSE']
    
    def can_schedule_hearings(self):
        """Check if user can schedule hearings"""
        return self.user_type in ['JUDGE', 'COURT_STAFF', 'MEDIATOR']

    class Meta:
        verbose_name = "Account"
        verbose_name_plural = "Accounts"
        ordering = ['-created_at']


class UserProfile(models.Model):
    """Extended profile information for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    middle_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
   
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True, default='India')
    
    
    years_of_experience = models.PositiveIntegerField(blank=True, null=True)
    specialization = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Area of legal specialization"
    )
    education = models.TextField(blank=True, help_text="Educational background")
    
    
    profile_picture = models.ImageField(
        upload_to='profile_pictures/', 
        blank=True, 
        null=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile of {self.user.username}"
    
    def get_full_name(self):
        """Return the full name of the user"""
        names = [self.first_name, self.middle_name, self.last_name]
        return ' '.join([name for name in names if name])
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


class UserRole(models.Model):
    """Model to track user roles in specific cases or contexts"""
    ROLE_CHOICES = [
        ('PETITIONER', 'Petitioner'),
        ('RESPONDENT', 'Respondent'),
        ('PROSECUTION', 'Prosecution'),
        ('DEFENSE', 'Defense'),
        ('MEDIATOR', 'Mediator'),
        ('JUDGE', 'Judge'),
        ('COURT_REPORTER', 'Court Reporter'),
        ('BAILIFF', 'Bailiff'),
        ('WITNESS', 'Witness'),
        ('EXPERT_WITNESS', 'Expert Witness'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roles')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    case_number = models.CharField(max_length=100, help_text="Associated case number")
    is_active = models.BooleanField(default=True)
    assigned_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, help_text="Additional notes about this role assignment")
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()} in Case {self.case_number}"
    
    class Meta:
        verbose_name = "User Role"
        verbose_name_plural = "User Roles"
        unique_together = ['user', 'role', 'case_number']




