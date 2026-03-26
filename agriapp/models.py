from django.db import models
from django.utils import timezone

class User_Detail(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15)
    password = models.CharField(max_length=20)
    
    def __str__(self):
        return self.name

class Categories(models.Model):
    categories = models.CharField(max_length=50)

    def __str__(self):
        return self.categories

class Equipment(models.Model):
    categories = models.ForeignKey(Categories, on_delete=models.CASCADE)
    user_id = models.IntegerField()
    name = models.CharField(max_length=50)
    rent = models.IntegerField()
    condition = models.CharField(max_length=50)
    year = models.CharField(max_length=50)
    brand = models.CharField(max_length=50)
    Description = models.TextField()
    image = models.ImageField(upload_to='static/uploadImages')
    status = models.CharField(max_length=20, default='Available')
    totalEarning = models.IntegerField(default=0)

    def __str__(self):
        return self.name
        

class Orders(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('payment_pending', 'Payment Pending'),
        ('canceled', 'Canceled'),
    ]
    
    owner_id = models.IntegerField()
    customer_id = models.IntegerField()
    product_id = models.IntegerField()
    Check_in = models.DateField()
    Check_out = models.DateField()
    rent = models.IntegerField()
    owner_address = models.CharField(max_length=100)
    customer_address = models.CharField(max_length=100)
    payment_mode = models.CharField(max_length=50, blank=True)
    payment_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending', choices=STATUS_CHOICES)
    requested_at = models.DateTimeField(default=timezone.now)
    response_date = models.DateTimeField(null=True, blank=True)
    total_amount = models.IntegerField(default=0)
    owner_remarks = models.TextField(blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.get_status_display()}"
    
    def get_days(self):
        """Calculate rental days"""
        return (self.Check_out - self.Check_in).days + 1
    
    def calculate_total(self):
        """Calculate total rental amount"""
        return self.rent * self.get_days()