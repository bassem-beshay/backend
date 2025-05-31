from django.contrib import admin
from .models import Order, OrderItem, Address
# Register your models here.
from django.contrib import admin
from .models import Order, OrderItem, Address

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'date']
    list_filter = ['status', 'date']
    search_fields = ['user__email', 'id']
    date_hierarchy = 'date'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'vendor', 'quantity', 'vendor_earning']
    list_filter = ['vendor', 'product']
    search_fields = ['order__id', 'product__name', 'vendor__name']

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['street', 'city', 'state', 'postal_code', 'country']
    search_fields = ['street', 'city', 'postal_code']

