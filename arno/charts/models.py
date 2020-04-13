# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.
class FtpCredential(models.Model):
    name = models.CharField(max_length=1000, unique=True)
    host = models.CharField(max_length=1000)
    user = models.CharField(max_length=1000)
    pwd = models.CharField(max_length=1000)

    def __str__(self):
        return self.name


class SensorRecord(models.Model):
    source = models.ForeignKey(FtpCredential, on_delete=models.CASCADE)
    time = models.DateTimeField()
    data = models.TextField()

    def __str__(self):
        return '%s %s' % (self.source.name, self.time)
