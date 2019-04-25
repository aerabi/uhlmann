# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv
import os.path
import json

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from ftplib import FTP


def _cache_file_(filename):
    if os.path.exists(filename):
        return
    ftp = FTP(settings.FTP_URL)
    ftp.login(settings.FTP_USR, settings.FTP_PWD)
    localfile = open(filename, 'wb')
    ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
    ftp.quit()
    localfile.close()


def _color_(name):
    colors = {'solar': 'yellow', 'diesel': 'black', 'grid': 'red', 'consumption': 'green'}
    if name in colors:
        return colors[name]
    return 'red'


def _load_data_(filename, quarterly=False, multiplier=60):
    datasets = []
    keys = []
    colors = {'solar': 'yellow', 'diesel': 'black', 'analog': 'orange'}
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
                        'color': colors[simple_key] if simple_key in colors else 'red'
                    }
                    datasets.append(dataset)
            else:
                data = line.strip().split(';')
                if quarterly and int(data[0][-2:]) % 15 != 0:
                    continue
                for i in range(len(data) - 1):
                    scaled_data_point = str(float(data[i]) * multiplier) if i > 0 else data[i]
                    datasets[i % len(datasets)]['list'].append(scaled_data_point)
    for i in range(len(datasets)):
        datasets[i]['data'] = ', '.join(datasets[i]['list'])
    return datasets


def chart(request, filename):
    filename = '%s.CSV' % filename
    _cache_file_(filename)
    datasets = _load_data_(filename)
    context = {
        'labels': datasets[0]['list'],
        'datasets': datasets[1:],
    }
    return render(request, 'charts/chart.html', context)


def _load_solar_data_(labels, solar_max=1000):
    with open('solar.json', 'r') as json_file:
        solar_data_map = json.load(json_file)
    solar_data = [solar_data_map[label] * solar_max / 1000
                  if label in solar_data_map else 0
                  for label in labels]
    dataset = {
        'name': 'Solar [kW]',
        'data': ', '.join(map(str, solar_data)),
        'list': solar_data,
        'color': 'yellow'
    }
    return dataset


def demo(request, solar_max=1000):
    all_datasets = _load_data_('0225.CSV', quarterly=True)
    labels = all_datasets[0]['list']
    consumption_dataset = all_datasets[2]
    solar_dataset = _load_solar_data_(labels, int(solar_max))
    difference_data = [float(consumption_dataset['list'][i]) - solar_dataset['list'][i]
                       for i in range(len(solar_dataset['list']))]
    difference_dataset = {
        'name': 'Grid [kW]',
        'data': ', '.join(map(str, difference_data)),
        'list': difference_data,
        'color': 'green'
    }
    datasets = [consumption_dataset, solar_dataset, difference_dataset]
    context = {
        'labels': labels,
        'datasets': datasets,
    }
    return render(request, 'charts/chart.html', context)


def _str_(number):
    if number == 0:
        return ''
    return str(number)


def _simple_csv_loader_(columns, solar_index, consumption_index, solar_max=15000):
    datasets = [{'name': name, 'list': [], 'color': _color_(name)} for name in columns]
    labels = []
    with open('bernd.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        for row in csv_reader:
            adjusted_solar = float(row[solar_index]) * solar_max / 1000
            adjusted_consumption = float(row[consumption_index]) - adjusted_solar
            for index in range(len(row)):
                cell = row[index].strip()
                if index == 0:
                    labels.append(cell)
                elif index == solar_index:
                    datasets[index - 1]['list'].append(_str_(adjusted_solar))
                elif index == consumption_index:
                    datasets[index - 1]['list'].append(_str_(adjusted_consumption))
                elif columns[index - 1] == 'diesel':
                    scaled_diesel = float(cell) * (adjusted_consumption + adjusted_solar)
                    datasets[index - 1]['list'].append(_str_(scaled_diesel))
                else:
                    datasets[index - 1]['list'].append(cell)
    for i in range(len(datasets)):
        datasets[i]['data'] = ', '.join(datasets[i]['list'])
    return labels, datasets


def csv_based_demo(request, solar_max=15000):
    labels, datasets = _simple_csv_loader_(['solar', 'grid', 'consumption', 'diesel'], 1, 3, int(solar_max))
    context = {
        'labels': labels,
        'datasets': datasets,
    }
    return render(request, 'charts/chart.html', context)


def csv_based_demo_json(request, solar_max=15000):
    _, datasets = _simple_csv_loader_(['solar', 'grid', 'consumption', 'diesel'], 1, 3, int(solar_max))
    return JsonResponse({dataset['name']: dataset for dataset in datasets})
