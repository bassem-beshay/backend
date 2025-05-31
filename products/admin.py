from django.contrib import admin
from .models import Product, Category

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    list_per_page = 10
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        # ('Timestamps', {
        #     'fields': ('updated_at',),
        #     'classes': ('collapse',)
        # }),
    )
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('products')
    def get_products(self, obj):
        return ", ".join([product.name for product in obj.products.all()]) if obj.products.exists() else "No products"
    get_products.short_description = 'Products'
    get_products.admin_order_field = 'products'
    def has_add_permission(self, request):
        return request.user.is_superuser

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'price', 'stock', 'category', 'created_at', 'updated_at')
    search_fields = ('name', 'vendor__name')
    list_filter = ('category', 'is_active')
    ordering = ('-created_at',)
    list_per_page = 10
    fieldsets = (
        (None, {
            'fields': ('name', 'vendor', 'description', 'price', 'stock', 'category', 'image', 'discount', 'is_active')
        }),
        # ('Timestamps', {
        #     'fields': ('updated_at',), 
        #     'classes': ('collapse',)
        # }),
    )
    def has_add_permission(self, request):
        return request.user.is_superuser



admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)