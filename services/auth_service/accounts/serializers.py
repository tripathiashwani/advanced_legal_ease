
from rest_framework import serializers
from django.contrib.auth import get_user_model

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserProfile, UserRole

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'middle_name', 'date_of_birth',
            'address_line_1', 'address_line_2', 'city', 'state', 
            'zip_code', 'country', 'years_of_experience', 'specialization',
            'education', 'full_name'
        ]

class UserRoleSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = UserRole
        fields = ['role', 'role_display', 'case_number', 'is_active', 'assigned_date', 'notes']
        read_only_fields = ['assigned_date']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    roles = UserRoleSerializer(many=True, read_only=True)
    user_type_display = serializers.CharField(source='get_user_type_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'user_type', 'user_type_display',
            'bar_number', 'license_number', 'organization', 'phone_number',
            'is_verified', 'verification_date', 'created_at', 'updated_at',
            'profile', 'roles'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'verification_date']

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
   
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'confirm_password',
            'user_type', 'bar_number', 'license_number', 'organization',
            'first_name', 'last_name', 'phone_number'
        ]

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        
       
        legal_professional_types = ['PROSECUTION', 'DEFENSE', 'MEDIATOR', 'JUDGE']
        if data.get('user_type') in legal_professional_types:
            if not data.get('bar_number') and not data.get('license_number'):
                raise serializers.ValidationError(
                    "Professional credentials (bar number or license number) are required for legal professionals"
                )
        
        return data

    def create(self, validated_data):
       
        profile_data = {
            'first_name': validated_data.pop('first_name', ''),
            'last_name': validated_data.pop('last_name', ''),
        }
        validated_data.pop('confirm_password', None)
        
       
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            user_type=validated_data.get('user_type', 'OBSERVER'),
            bar_number=validated_data.get('bar_number', ''),
            license_number=validated_data.get('license_number', ''),
            organization=validated_data.get('organization', ''),
            phone_number=validated_data.get('phone_number', ''),
        )
        
        
        UserProfile.objects.create(user=user, **profile_data)
        
        return user

class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['user_type'] = user.user_type
        token['is_verified'] = user.is_verified
        return token

class UserRoleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ['user', 'role', 'case_number', 'notes']
    
    def validate(self, data):
        if not data['user']:
            raise serializers.ValidationError("User is required")
        if not data['role']:
            raise serializers.ValidationError("Role is required")
        if not data['case_number']:
            raise serializers.ValidationError("Case number is required")
        if UserRole.objects.filter(
            user=data['user'],
            role=data['role'],
            case_number=data['case_number'],
            is_active=True
        ).exists():
            raise serializers.ValidationError(
                f"User already has the role {data['role']} for case {data['case_number']}"
            )
        return data

