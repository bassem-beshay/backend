from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.throttling import UserRateThrottle
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from psycopg2.errors import UniqueViolation
import logging

from .models import Vendor
from .serializers import VendorSerializer, VendorPublicSerializer
from .permissions import IsOwnerOfVendor

logger = logging.getLogger(__name__)


class VendorThrottle(UserRateThrottle):
    rate = '100/day'
    scope = 'vendor_operations'


class VendorViewSet(viewsets.ModelViewSet):
    serializer_class = VendorSerializer
    parser_classes = [MultiPartParser, FormParser] 
    throttle_classes = [VendorThrottle]

    def get_permissions(self):
        if self.action in ['create', 'retrieve', 'update', 'partial_update', 'destroy', 'deactivate']:
            return [permissions.IsAuthenticated(), IsOwnerOfVendor()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        user = self.request.user
        if self.action == 'list':
            return Vendor.objects.filter(is_verified=True, is_active=True).select_related('user').prefetch_related('products')

        if user and not isinstance(user, AnonymousUser):
            if user.is_staff:
                return Vendor.objects.all()
            return Vendor.objects.filter(user=user)

        return Vendor.objects.none()

    def get_serializer_class(self):
        if self.action == 'list':
            return VendorPublicSerializer
        return VendorSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page or queryset, many=True)
        return self.get_paginated_response(serializer.data) if page else Response(serializer.data)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            if hasattr(request.user, 'vendor'):
                raise ValidationError({'detail': 'You already have a vendor account.'})

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        except ValidationError as ve:
            logger.warning(f"Validation error: {ve.detail}")
            return Response(ve.detail, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError as ie:
            error_message = "Duplicate entry." if isinstance(ie.__cause__, UniqueViolation) else "Database integrity error."
            logger.error(f"IntegrityError: {ie}")
            return Response({"detail": error_message}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.exception("Unexpected error during vendor creation.")
            return Response({"detail": "Unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def toggle_store_sctive_status(self, request, pk=None):
        vendor = Vendor.objects.filter(user=request.user).first()
        if not vendor:
            raise PermissionDenied("You do not own a vendor account.")

        vendor.is_active = not vendor.is_active
        vendor.save()

        status_text = 'deactivated' if not vendor.is_active else 'activated'
        return Response({'status': f'Vendor account {status_text}.'}, status=status.HTTP_200_OK)


    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def storedetails(self, request):
        try:
            vendor = Vendor.objects.get(user=request.user)
            serializer = self.get_serializer(vendor)
            return Response(serializer.data)
        except Vendor.DoesNotExist:
            return Response({'detail': 'Vendor not found'}, status=404)
