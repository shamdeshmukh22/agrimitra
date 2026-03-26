from django import forms
from .models import User_Detail, Equipment, Categories, Orders
class Sign_up(forms.ModelForm):
    class Meta:
         model=User_Detail
         fields='__all__'
         widgets ={
              'name': forms.TextInput(attrs={'class': 'form-control bg-light '}),
              'email': forms.EmailInput(attrs={'class': 'form-control bg-light '}),
              'mobile': forms.NumberInput(attrs={'class': 'form-control bg-light '}),
              'password': forms.PasswordInput(attrs={'class': 'form-control bg-light '}),

         }

class Login(forms.ModelForm):
     class Meta:
           model=User_Detail
           fields={'email','password'}
           widgets ={
              'email': forms.EmailInput(attrs={'class': 'form-control bg-light '}), 
              'password': forms.PasswordInput(attrs={'class': 'form-control bg-light '}),

         }
           
class EquipmentForm(forms.ModelForm):
    # Field ko yahan define karein, lekin queryset empty rakhein
    categories = forms.ModelChoiceField(
        queryset=Categories.objects.none(), 
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    def __init__(self, *args, **kwargs):
        super(EquipmentForm, self).__init__(*args, **kwargs)
        try:
            # Queryset ko yahan update karein logic ke saath
            self.fields['categories'].queryset = Categories.objects.all()
            
            # Dropdown mein dikhne wala text set karein
            self.fields['categories'].label_from_instance = lambda obj: f"{obj.categories}"
        except Exception:
            # Agar koi error aaye (table missing etc.), toh queryset empty rakhein
            self.fields['categories'].queryset = Categories.objects.none()

    class Meta:
        model = Equipment
        fields = ['categories', 'name', 'rent', 'condition', 'year', 'brand', 'Description', 'image']
        # Baki widgets yahan pehle ki tarah rahenge...
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter equipment name'
            }),
            'rent': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'condition': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'year': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'brand': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'Description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }


class RentalRequestForm(forms.ModelForm):
    Check_in = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Check-in Date'
    )
    Check_out = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Check-out Date'
    )
    
    customer_address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter your complete address'
        }),
        label='Your Address'
    )

    class Meta:
        model = Orders
        fields = ['Check_in', 'Check_out', 'customer_address']


class PaymentForm(forms.Form):
    PAYMENT_MODE_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('upi', 'UPI'),
        ('netbanking', 'Net Banking'),
    ]
    
    payment_mode = forms.ChoiceField(
        choices=PAYMENT_MODE_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label='Payment Method'
    )