from django.utils import timezone
from django.contrib import admin
from .models import Vendor
from .tasks import send_vendor_approval_email, send_vendor_rejection_email
from django.http import HttpResponse

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('store_name', 'user', 'is_verified', 'is_active', 'created_at')
    list_filter = ('is_verified', 'is_active')
    search_fields = ('store_name', 'user__username')
    ordering = ('-created_at',)
    counter = 0 
    actions = ['approve_vendors', 'reject_vendors', "activeate_vendors", "deactivate_vendors"]

    def approve_vendors(self, request, queryset):
        counter = 0
        for vendor in queryset:
            if not vendor.is_verified:
                vendor.is_verified = True
                vendor.verified_at = timezone.now()
                vendor.save()
                counter += 1
                # Send approval email
                send_vendor_approval_email(vendor.id)
                
        if counter  > 0: 
            self.message_user(request, f"{queryset.count()} vendor(s) approved and notified.")
    approve_vendors.short_description = "Approve selected vendors"

    def reject_vendors(self, request, queryset):
        counter = 0
        for vendor in queryset:
            if vendor.is_verified:
                vendor.is_verified = False
                vendor.rejection_reason = "Rejected via admin panel"
                vendor.save()
                counter += 1
                # Send rejection email
                send_vendor_rejection_email(vendor.id, vendor.rejection_reason)
        
        if counter  > 0:
            self.message_user(request, f"{queryset.count()} vendor(s) rejected and notified.")
    reject_vendors.short_description = "Reject selected vendors"


    def activeate_vendors(self, request, queryset):
        counter = 0
        for vendor in queryset:
            if not vendor.is_active:
                vendor.is_active = True
                vendor.save()
                counter += 1
        
        if counter  > 0:
            self.message_user(request, f"{queryset.count()} Vendor(s) activated.")

    activeate_vendors.short_description = "Activeate Selected Vendors"


    def deactivate_vendors(self, request, queryset):
        counter = 0
        for vendor in queryset:
            if vendor.is_active:
                vendor.is_active = False
                vendor.save()
                counter += 1
        
        if counter  > 0:
            self.message_user(request, f"{queryset.count()} Vendor(s) deactivated.")

    deactivate_vendors.short_description = "Deactiveate Selected Vendors"