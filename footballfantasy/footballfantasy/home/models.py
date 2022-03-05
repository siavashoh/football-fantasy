from datetime import datetime

from django.contrib.admin.options import ModelAdmin
from createteam.models import League
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
# Create your models here.


class Log(models.Model):
    # "title" : "Unexpected exception!"
    title = models.CharField(max_length=100)
    # "message" : "Undefined segmenter method: 2"
    message = models.CharField(max_length=500)
    # "data" : {, "User_id" : "1234", "whare": "createteam:view:(change or create or x y) ", "exeption_message" : "abc", ... }
    data = models.JSONField()
    # "created_at" : 1622444365,
    create_at = models.DateTimeField(default=datetime.now())
    # "is_info" : false,
    is_info = models.BooleanField(default=False)
    # "is_error" : true,
    is_error = models.BooleanField(default=False)
    # "is_wanring" : false,
    is_warning = models.BooleanField(default=False)
    
    def __str__(self):
        return "%s | %s | %s | %s" % (self.title, self.message, self.create_at, self.data)
 