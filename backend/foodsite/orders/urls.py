from django.urls import path
from .views import *

urlpatterns = [
    path('items/', ItemListView.as_view(), name='item-list'),
    path('cart/', CartDetailView.as_view(), name='cart-detail'),
    path('carts/', CartView.as_view(), name='user-cart'),
    path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),
    path('cart/decrease/', DecreaseItemView.as_view(), name='decrease-cart-item'),
    path('cart/item/<int:item_id>/', RemoveCartItemView.as_view(), name='remove-from-cart'),
       path('place-order/', PlaceOrder.as_view(), name='place-order'),
    path('track-order/', TrackOrderView.as_view(), name='track-order'),
    path('search/', SearchItemsView.as_view(), name='search_items'),
        path('addresses/', UserAddressesView.as_view(), name='user-addresses'),
        path('registers/', RegisterVendorView.as_view(), name='register_vendor'),
         path('check-email/', CheckEmailExistsView.as_view(), name='check-email'),
         path('payment/',PaymentView.as_view(),name='payment')

]
