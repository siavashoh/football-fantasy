from django.urls import path
from . import views

app_name='createteam'

urlpatterns = [
    path("<task>/<league_id>/<hash>", views.create_team, name="createteam"),
    path("chooseleague/<hello>", views.choose_league, name="chooseleague"),
]