from django.db import models
from django.conf import settings

# Create your models here.
def get_upload_path(instance, filename):
    # Generate a unique upload path for the vendor logo
    return f'vendor_logos/{instance.user.id}/{filename}'

class Vendor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    store_name = models.CharField(max_length=255, unique=True)
    store_description = models.TextField()
    store_logo = models.ImageField(upload_to=get_upload_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    contact_phone = models.CharField(max_length=15)
    contact_email = models.EmailField()
    
 
    def __str__(self): 
        return self.store_name
    
