from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

# Register your models here.

from .models import User as Account, UserProfile, UserRole

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    extra = 0

class UserRoleInline(admin.TabularInline):
    model = UserRole
    extra = 0
    readonly_fields = ('assigned_date',)

@admin.register(Account)
class AccountAdmin(BaseUserAdmin):
    list_display = (
        'username', 
        'email', 
        'user_type', 
        'is_verified',
        'organization',
        'created_at'
    )
    list_filter = (
        'user_type', 
        'is_verified', 
        'is_staff', 
        'is_active',
        'created_at'
    )
    search_fields = ('username', 'email', 'bar_number', 'organization')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'verification_date')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Legal Platform Info', {
            'fields': (
                'user_type',
                'bar_number',
                'license_number',
                'organization',
                'phone_number',
                'is_verified',
                'verification_date',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Legal Platform Info', {
            'fields': (
                'user_type',
                'email',
                'bar_number',
                'license_number',
                'organization',
                'phone_number',
            )
        }),
    )
    
    inlines = [UserProfileInline, UserRoleInline]
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'get_full_name',
        'city',
        'state',
        'specialization',
        'years_of_experience'
    )
    list_filter = ('country', 'state', 'specialization')
    search_fields = (
        'user__username',
        'first_name',
        'last_name',
        'city',
        'specialization'
    )
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Personal Information', {
            'fields': (
                'first_name',
                'middle_name',
                'last_name',
                'date_of_birth'
            )
        }),
        ('Address', {
            'fields': (
                'address_line_1',
                'address_line_2',
                'city',
                'state',
                'zip_code',
                'country'
            )
        }),
        ('Professional Information', {
            'fields': (
                'years_of_experience',
                'specialization',
                'education'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'role',
        'case_number',
        'is_active',
        'assigned_date'
    )
    list_filter = ('role', 'is_active', 'assigned_date')
    search_fields = ('user__username', 'case_number', 'role')
    readonly_fields = ('assigned_date',)
    
    fieldsets = (
        ('Role Assignment', {
            'fields': (
                'user',
                'role',
                'case_number',
                'is_active'
            )
        }),
        ('Additional Information', {
            'fields': (
                'notes',
                'assigned_date'
            )
        }),
    )