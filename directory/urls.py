from django.urls import path, re_path
from . import views

app_name = 'directory'

urlpatterns = [
    path("health/", views.health_check, name="health_check"),
    path("directory/", views.directory_list, name="directory_list"),
    re_path(r"^media/(?P<path>.*)$", views.protected_media, name="protected_media"),
]
