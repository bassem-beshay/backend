from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsVendorOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):

        # Read permissions are allowed for any authenticated user
        if request.method in SAFE_METHODS:
            return True
        
        return request.user.is_superuser or obj.vendor.user == request.user
