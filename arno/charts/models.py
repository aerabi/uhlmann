# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.
class FtpCredential(models.Model):
    name = models.CharField(max_length=1000, unique=True)
    host = models.CharField(max_length=1000)
    user = models.CharField(max_length=1000)
    pwd = models.CharField(max_length=1000)
