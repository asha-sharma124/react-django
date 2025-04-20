from django.contrib import admin
from .models import *
# Register your models here.
from django.contrib import admin
from .models import Item



admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Address)



from django.contrib import admin
from .models import Vendor, Item

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'location', 'is_approved']
    list_filter = ['is_approved']


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category']
    list_filter = ['category']