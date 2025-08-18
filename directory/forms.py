from django import forms
from django.core.exceptions import ValidationError
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['family', 'phone', 'address', 'photo', 'opt_in_directory', 'visible_name']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'visible_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            # Check file size (25MB = 25 * 1024 * 1024 bytes)
            max_size = 25 * 1024 * 1024
            if photo.size > max_size:
                raise ValidationError(
                    f'Photo file size must be under 25MB. Current size: {photo.size / (1024*1024):.1f}MB'
                )
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if photo.content_type not in allowed_types:
                raise ValidationError(
                    'Please upload a valid image file (JPEG, PNG, or GIF).'
                )
        
        return photo
