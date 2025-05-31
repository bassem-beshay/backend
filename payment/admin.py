from django.contrib import admin
from .models import Payment ,PaymentMethod
# Register your models here.
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'status', 'created_at') 

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['user', 'payment_type', 'provider', 'is_default', 'created_at']
    list_filter = ['payment_type', 'is_default']
    search_fields = ['user__email', 'provider']