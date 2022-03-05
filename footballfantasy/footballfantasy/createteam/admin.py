from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Player)
admin.site.register(models.Team)
admin.site.register(models.League)
admin.site.register(models.Team_Player)
admin.site.register(models.League_Player_Score)
admin.site.register(models.League_Player_Change_Dates)
