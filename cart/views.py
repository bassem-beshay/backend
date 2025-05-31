from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from products.models import Product
from django.core.exceptions import ValidationError
from django.core.cache import cache



class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_cache_key(self):
        return f"user_{self.request.user.id}_cart"

    def get_queryset(self):
        cache_key = self.get_cache_key()
        cached_cart = cache.get(cache_key)
        
        if cached_cart is not None:
            return cached_cart
        
        cart = Cart.objects.filter(user=self.request.user)
        cache.set(cache_key, cart, timeout=60*60*24*2)  # Cache for 2 days
        return cart


   

    def get_object(self):
        cache_key = self.get_cache_key()
        cached_cart = cache.get(cache_key)
        
        if cached_cart is not None:
            return cached_cart[0] if cached_cart else None
        
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        cache.set(cache_key, [cart], timeout=60*15)
        return cart

    def invalidate_cache(self):
        cache_key = self.get_cache_key()
        cache.delete(cache_key)

    @action(detail=False, methods=["get"])
    def my_cart(self, request):
        cart = self.get_object()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def add_item(self, request):
        product_id = request.data.get("product")
        quantity = int(request.data.get("quantity", 1))
        
        if not product_id:
            return Response(
                {"error": "Product ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, 
            product=product
        )
        
        if created:
            cart_item.quantity = quantity  
        else:
            cart_item.quantity += quantity  

        try:
            cart_item.full_clean()
            cart_item.save()
            self.invalidate_cache()  # Clear cache after modification
        except ValidationError as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False, 
        methods=["delete"], 
        url_path="remove_item/(?P<product_id>[^/.]+)"
    )
    def remove_item(self, request, product_id=None):
        cart = self.get_object()

        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.delete()
            self.invalidate_cache()  # Clear cache after modification
            return Response(
                {"detail": "product removed from cart"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except CartItem.DoesNotExist:
            return Response(
                {"detail": "product not found in cart"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(
        detail=False, 
        methods=["patch"], 
        url_path="update_item/(?P<product_id>[^/.]+)"
    )
    @action(
    detail=False, 
    methods=["patch"], 
    url_path="update_item/(?P<product_id>[^/.]+)"
)
    def update_item(self, request, product_id=None):
        cart = self.get_object()
        quantity = request.data.get("quantity")

        # Validate quantity
        try:
            quantity = int(quantity)
            if quantity < 1:
                return Response(
                    {"detail": "Quantity must be at least 1"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (TypeError, ValueError):
            return Response(
                {"detail": "Invalid quantity provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.quantity = quantity
            
            # This will trigger your clean() method which checks stock
            cart_item.full_clean()  
            cart_item.save()
            
            self.invalidate_cache()  # Clear cache after modification
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data)
            
        except CartItem.DoesNotExist:
            return Response(
                {"detail": "product not found in cart"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValidationError as e:
            return Response(
                {"detail": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )