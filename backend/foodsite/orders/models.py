from django.db import models
from users.models import CustomUser
class Vendor(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    location = models.CharField(max_length=255)
    is_approved = models.BooleanField(default=False)  # Only approved vendors are usable
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Item(models.Model):
    CATEGORY_CHOICES = [
        ('festival', 'Festival Specific'),
        ('fast_food', 'Fast Food'),
        ('main_course', 'Main Course'),
        ('sweets', 'Sweets'),
        ('drinks', 'Drinks'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.FloatField()
    image = models.ImageField(upload_to='items/')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='main_course') 
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
 # add this line
    def __str__(self):
        return self.name
    

class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE,null=True)
    items = models.ManyToManyField(Item, through='CartItem')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.item.name}"


class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    items = models.ManyToManyField(Item, through='OrderItem')
    status = models.CharField(max_length=20, default="Confirmed")  # Order status (e.g., confirmed, shipped, delivered)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_amount = models.FloatField()

    def __str__(self):
        return f"Order {self.id} for {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.item.name}"
    


from django.db import models


class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='addresses')
    lane = models.CharField(max_length=255)
    nearby_location = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lane}, {self.nearby_location}, {self.city} - {self.pincode}"
