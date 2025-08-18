from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.conf import settings
from pathlib import Path
from .models import Profile

# Create your views here.

@login_required
def directory_list(request):
    """Display directory of approved and opted-in profiles"""
    qs = (Profile.objects
          .filter(parish__slug="st-edward", opt_in_directory=True, approved=True)
          .select_related("family", "user")
          .order_by("family__name", "user__last_name", "user__first_name"))
    
    return render(request, "directory/list.html", {"profiles": qs})

@login_required
def protected_media(request, path):
    """Serve media files only to authenticated users"""
    base = Path(settings.MEDIA_ROOT)
    full = (base / path).resolve()
    
    # Security check: ensure path is within MEDIA_ROOT
    if not str(full).startswith(str(base.resolve())) or not full.exists():
        raise Http404
    
    return FileResponse(open(full, "rb"))
