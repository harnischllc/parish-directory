from django.urls import path, re_path
from . import views

urlpatterns = [
    path("directory/", views.directory_list, name="directory"),  # will implement
    re_path(r"^media/(?P<path>.*)$", views.protected_media, name="protected_media"),  # will implement
]
