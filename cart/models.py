from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from products.models import Product
import logging

logger = logging.getLogger(__name__)

class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart"
    )
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def __str__(self):
        return f"Cart of {self.user.username}"

    @property
    def total_price(self):
        cache_key = f"cart_{self.id}_total_price"
        cached_total = cache.get(cache_key)
        
        if cached_total is not None:
            return cached_total
            
        total = sum(item.total_price for item in self.items.all())
        cache.set(cache_key, total, timeout=60*15)  # Cache for 15 minutes
        return total

    @property
    def total_quantity(self):
        cache_key = f"cart_{self.id}_total_quantity"
        cached_quantity = cache.get(cache_key)
        
        if cached_quantity is not None:
            return cached_quantity
            
        quantity = sum(item.quantity for item in self.items.all())
        cache.set(cache_key, quantity, timeout=60*15)
        return quantity

    def get_cache_keys(self):
        return [
            f"cart_{self.id}_total_price",
            f"cart_{self.id}_total_quantity",
            f"user_{self.user_id}_cart"
        ]

    def invalidate_cache(self):
        """Clear all cache entries related to this cart"""
        keys = self.get_cache_keys()
        cache.delete_many(keys)
        logger.debug(f"Invalidated cache for cart {self.id}")

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    # added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"

    @property
    def total_price(self):
        cache_key = f"cartitem_{self.id}_total_price"
        cached_price = cache.get(cache_key)
        
        if cached_price is not None:
            return cached_price
            
        price = self.product.price * self.quantity
        cache.set(cache_key, price, timeout=60*15)
        return price

    def clean(self):
        if self.quantity > self.product.stock:
            raise ValidationError("The requested quantity is not available in stock")

    def invalidate_cache(self):
        """Clear cache entries related to this item and parent cart"""
        keys = [
            f"cartitem_{self.id}_total_price",
            f"cart_{self.cart_id}_total_price",
            f"cart_{self.cart_id}_total_quantity",
            f"user_{self.cart.user_id}_cart"
        ]
        cache.delete_many(keys)
        logger.debug(f"Invalidated cache for cart item {self.id}")

# Signal handlers for cache invalidation
@receiver(post_save, sender=CartItem)
def invalidate_cart_cache_on_save(sender, instance, **kwargs):
    instance.invalidate_cache()
    instance.cart.invalidate_cache()

@receiver(post_delete, sender=CartItem)
def invalidate_cart_cache_on_delete(sender, instance, **kwargs):
    instance.invalidate_cache()
    instance.cart.invalidate_cache()

@receiver(post_save, sender=Cart)
def invalidate_cart_cache(sender, instance, **kwargs):
    instance.invalidate_cache()