import os
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from PIL import Image, ImageOps
from io import BytesIO

User = get_user_model()


def profile_photo_upload_path(instance, filename):
    """Generate upload path for profile photos: profiles/u<user_id>/<filename>"""
    ext = os.path.splitext(filename)[1]
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
    photo = models.ImageField(upload_to=profile_photo_upload_path, blank=True, null=True)
    opt_in_directory = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    visible_name = models.CharField(max_length=200, blank=True)
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
                    target_width, target_height = 600, 400
                    aspect_ratio = 600 / 400
                else:  # Portrait
                    target_width, target_height = 400, 600
                    aspect_ratio = 400 / 600
                
                # Calculate crop dimensions to maintain aspect ratio
                current_ratio = width / height
                if current_ratio > aspect_ratio:
                    # Image is wider than target ratio, crop width
                    new_width = int(height * aspect_ratio)
                    left = (width - new_width) // 2
                    img = img.crop((left, 0, left + new_width, height))
                elif current_ratio < aspect_ratio:
                    # Image is taller than target ratio, crop height
                    new_height = int(width / aspect_ratio)
                    top = (height - new_height) // 2
                    img = img.crop((0, top, width, top + new_height))
                
                # Resize to target dimensions using LANCZOS
                img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                
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
