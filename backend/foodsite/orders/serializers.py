from rest_framework import serializers
from .models import Item, Cart, CartItem,Order,OrderItem,Vendor

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['name', 'email', 'location']
class ItemSerializer(serializers.ModelSerializer):
    vendor = VendorSerializer()
    class Meta:
        model = Item
        fields = ['id', 'name', 'description', 'price', 'image','vendor']

class CartItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer()

    class Meta:
        model = CartItem
        fields = ['item', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items']

class OrderItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer()

    class Meta:
        model = OrderItem
        fields = ('item', 'quantity')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'status', 'created_at', 'total_amount', 'items')


from rest_framework import serializers
from .models import Address

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'lane', 'nearby_location', 'city', 'pincode']
