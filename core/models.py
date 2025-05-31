from django.db import models
from django.core.cache import cache

class SiteSetting(models.Model):
    currency = models.CharField(max_length=5, default="EGP")
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.set("site_currency", self.currency, timeout=60 * 60 * 24 * 7)  # 7 days

    def __str__(self):
        return f"Settings - Currency: {self.currency}"