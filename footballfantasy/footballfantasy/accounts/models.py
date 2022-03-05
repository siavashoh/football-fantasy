from django.db import models
from django.contrib.auth.models import User
from createteam.models import Team, League


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=11, blank=False, null=False)
    is_email_verified = models.BooleanField(default=False)
    is_team_created = models.BooleanField(default=False)

    def __str__(self):
        return "%s | %s | %s | %s" % (self.user.id, self.user.email, self.phone_number, str(self.is_email_verified))


class User_Team(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    players = models.JSONField(null=True)
    team_format = models.JSONField(null=True)
    main_players = models.JSONField(null=True)
    user_score = models.FloatField(default=0)
    is_changed = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.email