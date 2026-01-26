from django import forms
from .models import ChildProfile


class ChildLoginForm(forms.Form):
    """Form for child login with username and PIN"""
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username',
            'autofocus': True
        })
    )
    
    pin = forms.CharField(
        max_length=4,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your PIN',
            'pattern': '[0-9]{4}',
            'inputmode': 'numeric'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        pin = cleaned_data.get('pin')
        
        if username and pin:
            try:
                child = ChildProfile.objects.get(username__iexact=username)
                if child.pin != pin:
                    raise forms.ValidationError('Incorrect username or PIN. Please try again.')
                cleaned_data['child'] = child
            except ChildProfile.DoesNotExist:
                raise forms.ValidationError('Incorrect username or PIN. Please try again.')
        
        return cleaned_data


class ChildProfileForm(forms.ModelForm):
    """Form for creating/editing child profiles"""
    
    pin = forms.CharField(
        max_length=4,
        min_length=4,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 4-digit PIN',
            'pattern': '[0-9]{4}',
            'title': 'PIN must be exactly 4 digits'
        }),
        help_text='Create a 4-digit PIN for your child to login',
        required=False
    )
    
    pin_confirm = forms.CharField(
        max_length=4,
        min_length=4,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm PIN',
            'pattern': '[0-9]{4}',
        }),
        help_text='Enter the PIN again to confirm',
        required=False
    )
    
    class Meta:
        model = ChildProfile
        fields = ['username', 'age_range', 'avatar']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a fun username for your child'
            }),
            'age_range': forms.Select(attrs={
                'class': 'form-control'
            }),
            'avatar': forms.RadioSelect()
        }
        help_texts = {
            'username': 'This will be displayed when your child logs in',
            'age_range': 'Select the age group that best fits your child',
            'avatar': 'Choose a career avatar - helps kids explore different life skills!'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing, make PIN optional
        if self.instance and self.instance.pk:
            self.fields['pin'].help_text = 'Leave blank to keep current PIN'
            self.fields['pin_confirm'].help_text = 'Leave blank to keep current PIN'
        else:
            self.fields['pin'].required = True
            self.fields['pin_confirm'].required = True
    
    def clean_username(self):
        """Ensure username is unique (except when editing the same child)"""
        username = self.cleaned_data.get('username')
        # Check if username exists, excluding the current instance when editing
        existing = ChildProfile.objects.filter(username__iexact=username)
        if self.instance and self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise forms.ValidationError('This username is already taken. Please choose another.')
        return username
    
    def clean(self):
        """Validate that PINs match and are numeric"""
        cleaned_data = super().clean()
        pin = cleaned_data.get('pin')
        pin_confirm = cleaned_data.get('pin_confirm')
        
        if pin and pin_confirm:
            if pin != pin_confirm:
                raise forms.ValidationError('PINs do not match. Please try again.')
            
            if not pin.isdigit():
                raise forms.ValidationError('PIN must contain only numbers.')
        
        return cleaned_data
