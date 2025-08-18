from django.contrib import admin
from .models import Parish, Family, Profile

@admin.register(Parish)
class ParishAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ('name', 'parish', 'slug')
    list_filter = ('parish',)
    search_fields = ('name', 'parish__name')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'family', 'parish', 'opt_in_directory', 'approved', 'created_at')
    list_filter = ('approved', 'opt_in_directory', 'parish')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'family__name')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'parish', 'family', 'visible_name')
        }),
        ('Contact Information', {
            'fields': ('phone', 'address')
        }),
        ('Directory Settings', {
            'fields': ('opt_in_directory', 'approved')
        }),
        ('Photo', {
            'fields': ('photo',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'family', 'parish')
