from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Setting(models.Model):
    name = models.CharField(max_length=90)
    value = models.CharField(max_length=30)
    
    def __str__(self):              # __unicode__ on Python 2
        return self.name
