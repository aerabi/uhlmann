# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

import math


def chart(request):
    context = {
        'labels': ['%d.12.2017' % day for day in range(1, 13)],
        'datasets': [
            {'name': 'Cosine', 'data': ', '.join([str(math.cos(i)) for i in range(1, 13)]), 'color': 'red'},
            {'name': 'Sine', 'data': ', '.join([str(math.sin(i)) for i in range(1, 13)]), 'color': 'blue'},
        ]
    }
    return render(request, 'charts/chart.html', context)
