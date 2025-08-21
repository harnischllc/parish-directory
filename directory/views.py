from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, JsonResponse, HttpResponse
from django.conf import settings
from pathlib import Path
from .models import Profile

def health_check(request):
    """Health check endpoint for Render.com monitoring"""
    return JsonResponse({"status": "ok"})

def home_redirect(request):
    """Redirect root path to the directory if logged in, else to login."""
    if request.user.is_authenticated:
        return redirect("directory:directory_list")
    return redirect("account_login")

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

def robots_txt(request):
    """Serve a restrictive robots.txt to prevent public indexing."""
    content = "User-agent: *\nDisallow: /\n"
    return HttpResponse(content, content_type="text/plain")
