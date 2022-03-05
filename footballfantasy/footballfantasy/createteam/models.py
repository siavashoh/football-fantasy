from datetime import datetime

from django.db import models
from django.contrib.auth.models import User 
from django.core.files.storage import FileSystemStorage
from django.db.models import base
from django.db.models.expressions import F


league_big_fs = FileSystemStorage(location='/media/images/leagues/big')
league_small_fs = FileSystemStorage(location='/media/images/leagues/small')
player_fs = FileSystemStorage(location='/media/images/players')
team_fs = FileSystemStorage(location='/media/images/Team')

class League(models.Model):
    league_name = models.CharField(max_length=50, blank=False, null=False)
    league_small_image = models.ImageField(upload_to='images/leagues/small/', blank=False, null=False)
    league_big_image = models.ImageField(upload_to='images/leagues/big/', blank=False, null=False)
    league_reward = models.ImageField(upload_to='images/leagues/reward/', blank=True, null=True)
    is_ended = models.BooleanField(default=False)
    end_date = models.DateTimeField()
    allow_to_create_team_date = models.DateTimeField()
    description = models.TextField(max_length=2000)
    allow_to_change_format_date = models.DateTimeField()
    next_change_format_date = models.DateTimeField(default=datetime.now())

    def __str__(self):
        return self.league_name


class Team(models.Model):
    team_name = models.CharField(max_length=100, blank=False, null=False)
    team_fullname = models.CharField(max_length=100, blank=False, null=False)
    league = models.ManyToManyField(League, related_name='Team_League')
    team_image = models.ImageField(blank=True, null=True, upload_to="images/teams/")

    def __str__(self):
        return self.team_name

    class Meta:
        ordering = ['team_name']


class Player(models.Model):
    firstname = models.CharField(max_length=100, blank=False, null=False)
    lastname = models.CharField(max_length=100, blank=False, null=False)
    fullname = models.CharField(max_length=150, blank=False, null=False)
    team_name = models.CharField(max_length=50, blank=False, null=False)
    score = models.FloatField(default=0)
    value = models.FloatField(default=0)
    player_image = models.ImageField(upload_to="images/players/", blank=True, null=True)

    # User_Player relation
    team = models.ManyToManyField(
        Team, through='Team_Player', blank=True)

    def __str__(self):
        return "%s %s" % (self.firstname, self.lastname)

    class Meta:
        ordering = ['firstname', 'lastname']


class League_Player_Score(models.Model):
    player= models.ForeignKey(Player, on_delete=models.CASCADE)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    score = models.FloatField(blank=False, null=False)
    date_added = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return "%s   %s   %s   %s"% (self.player, self.league, str(self.score), str(self.date_added))

class Team_Player(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    post = models.CharField(max_length=50, blank=False)

    def __str__(self) -> str:
        return "%s   |    %s    |    %s" % (self.player, self.team, self.post)

    class Meta:
        ordering = ['post', 'player']

class User_Team_Change(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    date = models.DateTimeField(blank=False, null=False)
    first_team = models.JSONField()
    second_team = models.JSONField()
    number_of_changes_allowed = models.IntegerField(default=0)


class League_Player_Change_Dates(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE, null=False, blank=False)
    start_ch_15 = models.DateTimeField()
    end_ch_15 = models.DateTimeField()
    start_ch_5 = models.DateTimeField()
    end_ch_5 = models.DateTimeField()

    def __str__(self):
        return self.league.league_name