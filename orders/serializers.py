from rest_framework import serializers
from .models import Address, Order, OrderItem


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ('id',)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'variant', 'vendor', 'quantity']
        read_only_fields = ['id']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value


class OrderSerializer(serializers.ModelSerializer):
    shipping_address = AddressSerializer()
    billing_address = AddressSerializer()
    items = OrderItemSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['id', 'status', 'date','user']

    def create(self, validated_data):
        shipping_data = validated_data.pop('shipping_address')
        billing_data = validated_data.pop('billing_address')
        items_data = validated_data.pop('items')

       
        shipping_address = Address.objects.create(**shipping_data)
        billing_address = Address.objects.create(**billing_data)

     
        user = self.context['request'].user

     
        order = Order.objects.create(
            user=user,
            shipping_address=shipping_address,
            billing_address=billing_address,
            **validated_data
        )

   
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order