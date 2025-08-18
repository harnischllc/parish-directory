import os
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from PIL import Image, ImageOps
from pathlib import Path

User = get_user_model()


def profile_photo_upload_path(instance, filename):
    """Generate upload path for profile photos: profiles/u<user_id>/<filename>"""
    return f"profiles/u{instance.user.id}/{filename}"


class Parish(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name_plural = "Parishes"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Family(models.Model):
    parish = models.ForeignKey(Parish, on_delete=models.CASCADE, related_name='families')
    name = models.CharField(max_length=200)
    slug = models.SlugField()
    
    class Meta:
        verbose_name_plural = "Families"
        unique_together = ['parish', 'slug']
    
    def __str__(self):
        return f"{self.name} ({self.parish.name})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    parish = models.ForeignKey(Parish, on_delete=models.CASCADE, related_name='profiles')
    family = models.ForeignKey(Family, on_delete=models.SET_NULL, null=True, blank=True, related_name='profiles')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    visible_name = models.CharField(max_length=200, blank=True)
    photo = models.ImageField(upload_to=profile_photo_upload_path, blank=True, null=True)
    opt_in_directory = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.parish.name}"
    
    def save(self, *args, **kwargs):
        # Process image if photo exists
        if self.photo:
            self._process_and_purge_image()
        
        super().save(*args, **kwargs)
    
    def _process_and_purge_image(self):
        """Process uploaded image: resize, crop to aspect ratio, and purge original"""
        try:
            # Open image with Pillow
            with Image.open(self.photo.path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Auto-rotate based on EXIF orientation
                img = ImageOps.exif_transpose(img)
                
                # Determine target dimensions based on orientation
                width, height = img.size
                if width >= height:  # Landscape
                    target_size = (600, 400)
                else:  # Portrait
                    target_size = (400, 600)
                
                # Use ImageOps.fit to maintain aspect ratio and crop to exact dimensions
                img = ImageOps.fit(img, target_size, method=Image.Resampling.LANCZOS)
                
                # Save over the original file with optimized JPEG settings
                img.save(
                    self.photo.path,
                    'JPEG',
                    quality=82,
                    optimize=True,
                    progressive=True
                )
                
        except Exception as e:
            # If image processing fails, raise validation error
            raise ValidationError(f"Image processing failed: {str(e)}")
    
    def get_visible_name_display(self):
        """Return visible name or fallback to user's name"""
        if self.visible_name:
            return self.visible_name
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
