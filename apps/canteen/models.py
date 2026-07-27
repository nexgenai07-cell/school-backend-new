from apps.common.models import BaseModel
from django.db import models


class Category(BaseModel):
    name = models.CharField(max_length=100, help_text="Food category")
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'categories'

    def __str__(self):
        return self.name


class MenuItem(BaseModel):
    name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='menu_items')
    is_available = models.BooleanField(default=True)

    class Meta:
        db_table = 'menu_items'

    def __str__(self):
        return self.name


class OrderItem(BaseModel):
    STATUS_CHOICES = [('placed', 'Placed'), ('served', 'Served'), ('cancelled', 'Cancelled')]

    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='canteen_orders')
    order_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='placed')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price at time of order")

    class Meta:
        db_table = 'order_items'

    def __str__(self):
        return f"{self.student} - {self.menu_item.name}"
