from django.db import models
from django.utils import timezone
# from .forms import Sign_up

class User_Detail(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15)
    password = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    address=models.CharField(max_length=200)
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
        ('extend_requested', 'Extension Requested'),
        ('reduce_requested', 'Early Return Requested'),
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
        """ Calculate rental days """
        return (self.Check_out - self.Check_in).days + 1
    
    def calculate_total(self):
        """Calculate total rental amount """
        return self.rent * self.get_days()

class RentalAdjustment(models.Model):
    ADJUSTMENT_TYPE_CHOICES = [
        ('extend', 'Extend Days'),
        ('reduce', 'Early Return'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
        ('completed', 'Completed'),
    ]

    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name='adjustments')
    adjustment_type = models.CharField(max_length=10, choices=ADJUSTMENT_TYPE_CHOICES)
    new_checkout_date = models.DateField()
    extra_days = models.IntegerField(default=0)    
    extra_amount = models.IntegerField(default=0)       
    status = models.CharField(max_length=10, default='pending', choices=STATUS_CHOICES)
    customer_note = models.TextField(blank=True)
    owner_remarks = models.TextField(blank=True)
    requested_at = models.DateTimeField(default=timezone.now)
    responded_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Adjustment #{self.id} [{self.adjustment_type}] for Order #{self.order.id}"

    def calculate_extra(self):
        """Calculate difference in days and amount vs original checkout"""
        diff = (self.new_checkout_date - self.order.Check_out).days
        self.extra_days = diff
        self.extra_amount = diff * self.order.rent
        return self.extra_days, self.extra_amount