# onboard urls
from django.urls import path
from . import views

app_name = 'onboard'
urlpatterns = [
    path("", views.onboard, name="onboard"),
]
