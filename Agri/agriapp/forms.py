from django import forms
from .models import User_Detail, Equipment, Categories, Orders, RentalAdjustment

class Sign_up(forms.ModelForm):
    class Meta:
         model=User_Detail
         fields='__all__'
         widgets ={
              'name': forms.TextInput(attrs={'class': 'form-control bg-light '}),
              'email': forms.EmailInput(attrs={'class': 'form-control bg-light '}),
              'mobile': forms.NumberInput(attrs={'class': 'form-control bg-light '}),
              'password': forms.PasswordInput(attrs={'class': 'form-control bg-light '}),
              'latitude': forms.HiddenInput( attrs={'id':'id_latitude'}),
            'longitude': forms.HiddenInput( attrs={'id':'id_longitude'}),
            'address': forms.TextInput( attrs={'id':'id_address'}),


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
    categories = forms.ModelChoiceField(
        queryset=Categories.objects.none(), 
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    def __init__(self, *args, **kwargs):
        super(EquipmentForm, self).__init__(*args, **kwargs)
        try:
            self.fields['categories'].queryset = Categories.objects.all()
            self.fields['categories'].label_from_instance = lambda obj: f"{obj.categories}"
        except Exception:
            self.fields['categories'].queryset = Categories.objects.none()

    class Meta:
        model = Equipment
        fields = ['categories', 'name', 'rent', 'condition', 'year', 'brand', 'Description', 'image']
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


class RentalAdjustmentForm(forms.Form):
    new_checkout_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='New Check-Out Date'
    )
    customer_note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Optional: reason for this request...'
        }),
        label='Note to Owner (Optional)'
    )
