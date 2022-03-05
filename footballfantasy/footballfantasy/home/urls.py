# onboard urls
from django.urls import path
from . import views

app_name = 'home'
urlpatterns = [
    path("<int:league_id>", views.home, name="home"),
]
