from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
import logging
from vendors.models import Vendor

logger = logging.getLogger(__name__)
User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    user_type = serializers.ChoiceField(choices=User.USER_TYPE_CHOICES)
    email = serializers.EmailField(required=True)
    name = serializers.CharField(required=True, max_length=255)
    username = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('name', 'email', 'username', 'password', 'password2', 'user_type', 'phone_number', 'address')

    def validate(self, attrs):
        logger.info(f"Validating registration data: {attrs}")
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # Check if email already exists
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists."})
        
        # Check if username already exists
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({"username": "A user with this username already exists."})
        
        return attrs

    def create(self, validated_data):
        logger.info(f"Creating user with data: {validated_data}")
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        user.is_verified = False
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

class UserSerializer(serializers.ModelSerializer):
    is_vendor = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'username', 'user_type', 'phone_number', 'address', 'is_verified','is_vendor')
        read_only_fields = ('id', 'is_verified')
    def get_is_vendor(self, obj):
        return hasattr(obj, 'vendor')

class PasswordResetSerializer(serializers.Serializer):
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs 

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs 