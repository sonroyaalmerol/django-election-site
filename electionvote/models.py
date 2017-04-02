from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Candidate(models.Model):
    name = models.CharField(max_length=90)
    nickname = models.CharField(max_length=30)
    description = models.TextField()
    votes = models.IntegerField(default=0)
    photourl = models.CharField(max_length=90)

    def __str__(self):              # __unicode__ on Python 2
        return self.name
