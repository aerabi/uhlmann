# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import FtpCredential
from .models import SensorRecord


# Register your models here.
admin.site.register(FtpCredential)
admin.site.register(SensorRecord)
