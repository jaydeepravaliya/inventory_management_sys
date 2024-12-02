from django.db import models
import random
import string
from django.contrib.auth.models import User
import uuid

class Product(models.Model):
    name = models.CharField(max_length=100, null=True)
    category = models.ForeignKey(
        "Category", on_delete=models.CASCADE, null=True
    )  # Link to Category
    stock_level = models.PositiveIntegerField(default=0)  # New field
    supplier = models.ForeignKey(
        "Supplier", on_delete=models.CASCADE, null=True
    )  # New field
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # New field

    def __str__(self):
        return f"{self.name}"


class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.category_name


class Supplier(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class StockTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('ADD', 'Add Stock'),
        ('REMOVE', 'Remove Stock'),
    ]

    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, to_field="username")

    # New Fields
    reference_number = models.CharField(max_length=12, unique=True, editable=False)
    remarks = models.CharField(max_length=255, blank=True, null=True)
    
    
    def __str__(self):
        return f'{self.transaction_type} - {self.product.name} ({self.quantity}) by {self.performed_by.username if self.performed_by else "Unknown"}'


    def save(self, *args, **kwargs):

        if not self.reference_number:
            # Generate reference number: 2 alphabets + 3 numbers + 1 alphabet + 1 number + 1 alphabet
            self.reference_number = (
                ''.join(random.choices(string.ascii_uppercase, k=2)) +  # 2 alphabets
                ''.join(random.choices(string.digits, k=3)) +           # 3 numbers
                random.choice(string.ascii_uppercase) +                 # 1 alphabet
                random.choice(string.digits) +                          # 1 number
                random.choice(string.ascii_uppercase)                   # 1 alphabet
            )

        if self.transaction_type == 'REMOVE':
            if self.product.stock_level < self.quantity:
                raise ValueError(f"Cannot remove {self.quantity} units. Only {self.product.stock_level} units available.")
            self.product.stock_level -= self.quantity
        elif self.transaction_type == 'ADD':
            self.product.stock_level += self.quantity

        self.product.save()  # Save the updated stock level
        super().save(*args, **kwargs)