from django import forms
from django.contrib.auth.models import User

from store.models import Order


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password != password_confirm:
            raise forms.ValidationError("Passwords do not match")


class CheckoutForm(forms.Form):
    checkout_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    checkout_email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    checkout_address = forms.CharField(widget=forms.Textarea, required=True)
    phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    additional_info = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = Order
        fields = ['checkout_name', 'checkout_email ', 'checkout_address ', 'phone', 'additional_info']
        widgets = {
            'checkout_name': forms.TextInput(attrs={'class': 'form-control'}),
            'checkout_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'checkout_address ': forms.Textarea(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'additional_info': forms.Textarea(attrs={'class': 'form-control'}),
        }