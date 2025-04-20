from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import ItemSerializer
from rest_framework.views import APIView
from django.shortcuts import render
from django.http import JsonResponse
from .models import *
# from .models import Cart, CartItem
from django.views.decorators.csrf import csrf_exempt
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from .forms import VendorRegistrationForm

from django.db.models import Q
from django.conf import settings
from django.http import JsonResponse

from .models import Vendor
from django.core.mail import send_mail
from django.conf import settings

from rest_framework import status
from django.utils import timezone
from datetime import timedelta

from django.shortcuts import get_object_or_404
from .serializers import *
import razorpay

class ItemListView(generics.ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category']






class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # Get the logged-in user from the request

        try:
            # Fetch the user's cart or create it if it doesn't exist
            cart, created = Cart.objects.get_or_create(user=user)
            cart_items = CartItem.objects.filter(cart=cart)  # Fetch the CartItems

            # Serialize the cart items
            cart_item_serializer = CartItemSerializer(cart_items, many=True)
            
            # Combine the cart data with the items
            cart_data = {
                'id': cart.id,
                'user': cart.user.id,
                'items': cart_item_serializer.data
            }

            return Response(cart_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": "Internal server error, please try again."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity', 1))

        item = get_object_or_404(Item, id=item_id)
        cart, _ = Cart.objects.get_or_create(user=user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)

        cart_item.quantity += quantity
        cart_item.save()

        return Response({"detail": "Item added"}, status=status.HTTP_200_OK)

class DecreaseItemView(APIView):
    def post(self, request):
        item_id = request.data.get('item_id')
        if not item_id:
            return Response({"error": "Item ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the user's cart (assuming the user is authenticated)
            cart = Cart.objects.get(user=request.user)

            # Retrieve the CartItem for the specific item in the user's cart
            cart_item = CartItem.objects.get(cart=cart, item_id=item_id)

            if cart_item.quantity > 1:
                # Decrease the quantity of the item
                cart_item.quantity -= 1
                cart_item.save()
            else:
                # If quantity is 1, remove the item from the cart
                cart_item.delete()

            # Re-fetch the updated cart items and total price
            cart_items = CartItem.objects.filter(cart=cart)
            total_price = sum(item.quantity * item.item.price for item in cart_items)

            # Serialize the updated cart items and return
            return Response({
                "cart_items": CartItemSerializer(cart_items, many=True).data,
                "total_price": total_price
            }, status=status.HTTP_200_OK)

        except Cart.DoesNotExist:
            return Response({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found in the cart."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error: {e}")
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class CartDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        cart_items = cart.cartitem_set.select_related('item')

        cart_data = []
        total_price = 0

        for item in cart_items:
            subtotal = item.item.price * item.quantity
            total_price += subtotal
            cart_data.append({
                "id": item.id,
                "item": {
                    "id": item.item.id,
                    "name": item.item.name,
                    "price": item.item.price,
                },
                "quantity": item.quantity,
                "total": subtotal
            })

        return Response({
            "cart_items": cart_data,
            "total_price": total_price
        })


class RemoveCartItemView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, item_id):
        print("aaaaaaaaaaa.....................aaaaaaaaaaaaaaaaaaaaaaaa")
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, cart=cart, item_id=item_id)
    
        cart_item.delete()
        return Response({"detail": "Item removed"}, status=status.HTTP_204_NO_CONTENT)
    

class PlaceOrder(APIView):
    def post(self, request):
        user = request.data.get('user_id')
        items_data = request.data.get('items')
        total_price = request.data.get('total_price')
        address = request.data.get('address')
        payment_method = request.data.get('payment_method')

        # Ensure there are items in the cart
        if not items_data:
            return Response({"error": "No items in cart."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the order
        order = Order.objects.create(user_id=user, total_amount=total_price, status="Confirmed")
        print("order",order)
        
        # Create order items
        for item_data in items_data:
            item = Item.objects.get(id=item_data['item_id'])
            order_item = OrderItem.objects.create(order=order, item=item, quantity=item_data['quantity'])
        
        # Now that the order is placed, delete the items from the cart
        try:
            cart = Cart.objects.get(user_id=user)  # Get the user's cart
            cart_items = CartItem.objects.filter(cart=cart)  # Get the cart items for the user

            # Delete the cart items
            cart_items.delete()

            # Optionally, you can also delete the cart if you don't need it anymore
            # cart.delete()

        except Cart.DoesNotExist:
            return Response({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Set the delivery time to 30 minutes from now
        delivery_time = timezone.now() + timedelta(minutes=30)

        # Prepare response data
        response_data = {
            'order_id': order.id,
            'delivery_time': delivery_time.strftime("%Y-%m-%d %H:%M:%S"),
            'order_items': [
                {
                    'item': item.item.name,
                    'quantity': item.quantity,
                    'price': item.item.price
                }
                for item in order.orderitem_set.all()  # Get the related order items
            ]
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

class TrackOrderView(APIView):
    permission_classes = [IsAuthenticated]  # Ensuring the user is authenticated

    def get(self, request, *args, **kwargs):
        print("in the track order...........................................................")
        try:
            # Fetch the most recent order for the logged-in user
            print(Order.objects.filter(user=request.user))
            order = Order.objects.filter(user=request.user).order_by('-created_at').first()
            print("order",order)

            if not order:
                return Response({'error': 'No orders found for this user'}, status=status.HTTP_404_NOT_FOUND)

            # Ensure that the `created_at` field is timezone-aware
            order_created_at = timezone.localtime(order.created_at)

            # Calculate the remaining time until delivery (e.g., 30 minutes from created_at)
            remaining_time = (order_created_at + timedelta(minutes=30) - timezone.now()).total_seconds()

            # Prevent negative remaining time
            remaining_time = max(remaining_time, 0)

            # Serialize the order with its items
            order_items = OrderItem.objects.filter(order=order)
            order_item_data = [
                {
                    'item': item.item.name,  # Assuming the item has a `name` attribute
                    'quantity': item.quantity,
                    'price': item.item.price  # Assuming the item has a `price` attribute
                }
                for item in order_items
            ]
            
            # Prepare the response data
            order_data = {
                'order_id': order.id,
                'status': order.status,
                'remaining_time': remaining_time,
                'items': order_item_data
            }

            return Response(order_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class SearchItemsView(APIView):
    def get(self, request):
        query = request.GET.get('q', '')
        if query:
            items = Item.objects.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        else:
            items = Item.objects.all()

        item_list = [
            {
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "price": item.price,
                "image": request.build_absolute_uri(item.image.url) if item.image else ""
            }
            for item in items
        ]

        return JsonResponse(item_list, safe=False)
    
from rest_framework import generics, permissions


class UserAddressesView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



from .serializers import VendorSerializer


class CheckEmailExistsView(APIView):
    def get(self, request, *args, **kwargs):
        email = request.GET.get('email')
        if email and Vendor.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': None}, status=status.HTTP_200_OK)

class RegisterVendorView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = VendorSerializer(data=request.data)
        
        if serializer.is_valid():
            # Save vendor instance, setting is_approved to False
            vendor = serializer.save(is_approved=False)
            
            # Send email to admin for approval
            send_mail(
                subject='New Vendor Registration Request',
                message=f"Vendor '{vendor.name}' registered.\nEmail: {vendor.email}\nLocation: {vendor.location}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL]
            )
            
            return Response({'message': 'Vendor submitted for approval'}, status=status.HTTP_201_CREATED)
        
        # Return errors if serializer is invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class PaymentView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        amount = request.data.get('amount')
        client = razorpay.Client(auth=('rzp_test_f2sIwDuER6xd3p', 'e8F3owJTPEGH8Rl6dJKP0PXR')) #api_key and api_secret
        order_data = {
            "amount": int(amount) * 100,  # convert to paise
            "currency": "INR",
            "payment_capture": 1
        }
        order = client.order.create(data=order_data)
        return Response(order)
