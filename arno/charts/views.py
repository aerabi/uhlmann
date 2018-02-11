# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os.path

from django.conf import settings
from django.shortcuts import render
from ftplib import FTP


def cache_file(filename):
    if os.path.exists(filename):
        return
    ftp = FTP(settings.FTP_URL)
    ftp.login(settings.FTP_USR, settings.FTP_PWD)
    localfile = open(filename, 'wb')
    ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
    ftp.quit()
    localfile.close()


def chart(request, filename):
    filename = '%s.CSV' % filename
    datasets = []
    keys = []
    colors = {'solar': 'yellow', 'diesel': 'black', 'analog': 'red'}
    cache_file(filename)
    with open(filename) as f:
        for line in f:
            if line[0] == '/':
                new_keys = [key.strip() for key in line[1:].strip().split(';')]
                for key in new_keys[:-1]:
                    if key in keys:
                        continue
                    keys.append(key)
                    simple_key = key.strip().split(' ')[0].lower()
                    dataset = {
                        'name': key,
                        'data': '',
                        'list': [],
                        'color': colors[simple_key] if simple_key in colors else 'blue'
                    }
                    datasets.append(dataset)
            else:
                data = line.strip().split(';')
                for i in range(len(data) - 1):
                    datasets[i % len(datasets)]['list'].append(data[i])
    for i in range(len(datasets)):
        datasets[i]['data'] = ', '.join(datasets[i]['list'])
    context = {
        'labels': datasets[0]['list'],
        'datasets': datasets[1:],
    }
    return render(request, 'charts/chart.html', context)
