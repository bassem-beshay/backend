from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError

def get_upload_path(instance, filename):
    vendor_id = instance.vendor.id if instance.vendor else 'default'
    return f'products/{vendor_id}/{filename}'

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_products(self):
        return self.products.all()
    

class Product(models.Model):
    vendor = models.ForeignKey('vendors.Vendor', related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock = models.IntegerField()
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to=get_upload_path) 
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.price} EGP"

    def clean(self):
        if self.price <= 0:
            raise ValidationError("Price must be greater than zero.")
        if self.stock < 0:
            raise ValidationError("Stock cannot be negative.")
        if self.discount < 0 or self.discount > 100:
            raise ValidationError("Discount must be between 0 and 100.")


    def save(self, *args, **kwargs):
        if self.discount > 0:
            if not self.original_price or self.original_price == 0:
                self.original_price = self.price
            discount_amount = (self.original_price * self.discount) / Decimal(100)
            self.price = self.original_price - discount_amount
        
        super().save(*args, **kwargs)