from django.urls import path

from . import views

urlpatterns = [
    path("welcome/<str:name>/", views.home),
    path("unique/", views.uniqueEndpoint),
    path("profile/<str:username>/", views.profile),
    path("", views.hello_world),
    path("<str:name>/", views.welcome_message)
]