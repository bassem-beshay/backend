from rest_framework import serializers
from django.core.validators import RegexValidator
from .models import Vendor
from django.utils import timezone
from rest_framework.exceptions import ValidationError

class VendorPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = [
            'id',
            'store_name',
            'store_description',
            'store_logo',
            'created_at'
        ]
        read_only_fields = fields

class VendorSerializer(serializers.ModelSerializer):
    """
    Full vendor serializer for owner/admin access with all fields and validations
    """
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    contact_phone = serializers.CharField(validators=[phone_regex], required=False)
    
    days_since_created = serializers.SerializerMethodField()
    is_owned_by_user = serializers.SerializerMethodField()
    
    class Meta:
        model = Vendor
        fields = [
            'id',
            'user',
            'store_name',
            'store_description',
            'store_logo',
            'contact_email',
            'contact_phone',
         
            'is_verified',
            'is_active',
            'created_at',
           
            'days_since_created',
            'is_owned_by_user'
        ]
        read_only_fields = (
            'id',
            'user',
            'is_verified',
            'is_active',
            'created_at',
            'days_since_created',
            'is_owned_by_user'
        )
        extra_kwargs = {
            'contact_email': {'required': True},
            'store_name': {
                'min_length': 3,
                'max_length': 100
            },
            'store_description': {
                'min_length': 10,
                'max_length': 500,    
            },
        }

    def get_days_since_created(self, obj):
        return (timezone.now() - obj.created_at).days if obj.created_at else None

    def get_is_owned_by_user(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.user == request.user
        return False

    def validate_store_name(self, value):
        if not value.strip():
            raise ValidationError("Store name cannot be empty or just whitespace")
        return value.strip()

    def validate_contact_email(self, value):
        if self.instance and self.instance.contact_email == value:
            return value
            
        if Vendor.objects.exclude(pk=self.instance.pk if self.instance else None)\
                         .filter(contact_email__iexact=value)\
                         .exists():
            raise ValidationError("This email is already associated with another vendor")
        return value.lower()

    def create(self, validated_data):
        validated_data.pop('user', None)
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        for field in ['user', 'is_verified', 'is_active', 'created_at']:
            validated_data.pop(field, None)
            
        if 'store_logo' in validated_data and validated_data['store_logo'] is None:
            instance.store_logo.delete(save=False)
            
        return super().update(instance, validated_data)