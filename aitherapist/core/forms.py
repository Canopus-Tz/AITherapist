# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile


class CustomUserCreationForm(UserCreationForm):
    """Enhanced user registration form"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes
        for fieldname in ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']:
            self.fields[fieldname].widget.attrs['class'] = 'form-control'
            
        # Update placeholders and help text
        self.fields['username'].widget.attrs['placeholder'] = 'Choose a username'
        self.fields['email'].widget.attrs['placeholder'] = 'your.email@example.com'
        self.fields['first_name'].widget.attrs['placeholder'] = 'First Name (Optional)'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last Name (Optional)'
        self.fields['password1'].widget.attrs['placeholder'] = 'Create a strong password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm your password'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Create user profile
            UserProfile.objects.create(user=user)
        return user


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile"""
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = UserProfile
        fields = ('bio', 'avatar')
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 4, 
                'class': 'form-control',
                'placeholder': 'Tell us a bit about yourself...'
            }),
            'avatar': forms.FileInput(attrs={'class': 'form-control'})
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Populate initial values and also ensure HTML value attribute is present
            # so fields always display current user data even if other rendering quirks occur.
            self.fields['first_name'].initial = user.first_name
            self.fields['first_name'].widget.attrs['value'] = user.first_name
            self.fields['first_name'].widget.attrs['placeholder'] = 'First Name'

            self.fields['last_name'].initial = user.last_name
            self.fields['last_name'].widget.attrs['value'] = user.last_name
            self.fields['last_name'].widget.attrs['placeholder'] = 'Last Name'

            self.fields['email'].initial = user.email
            self.fields['email'].widget.attrs['value'] = user.email
            self.fields['email'].widget.attrs['placeholder'] = 'your.email@example.com'
            
        # Add Bootstrap classes
        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        
        # Update user fields
        if hasattr(self, 'cleaned_data'):
            user = profile.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            if commit:
                user.save()
        
        if commit:
            profile.save()
        return profile


class ChatMessageForm(forms.Form):
    """Form for chat messages (used for CSRF protection)"""
    message = forms.CharField(
        max_length=1000,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Type your message here...',
            'id': 'message-input'
        })
    )