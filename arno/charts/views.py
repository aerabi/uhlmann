# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv
import os.path
import json

from collections import defaultdict

from django.conf import settings
from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import render
from ftplib import FTP


def _cache_file_(filename, hard_reload=True):
    if os.path.exists(filename) and not hard_reload:
        return
    ftp = FTP(settings.FTP_URL)
    ftp.login(settings.FTP_USR, settings.FTP_PWD)
    localfile = open(filename, 'wb')
    try:
        ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
        localfile.close()
    except:
        localfile.close()
        os.remove(filename)
    finally:
        ftp.quit()


def _color_(name):
    colors = {'solar': 'yellow', 'diesel': 'black', 'grid': 'red', 'consumption': 'green', 'export': 'green'}
    for substring in sorted(name.lower().strip().split(' ')):
        if substring in colors:
            return colors[substring]
    return 'red'


def _load_data_(filename, quarterly=True, multiplier=60, remove_zeros=False, acceptable_keys=None, group=1):
    acceptable_keys = acceptable_keys or ['solar in', 'solar export', 'load']
    datasets = {
        'time': {
            'name': 'time',
            'data': '',
            'list': [],
            'color': 'black'
        }
    }
    keys = []
    multipliers = defaultdict(float)
    grouped_datapoints = defaultdict(float)
    with open(filename, newline='') as f:
        csv_reader = csv.reader(f, delimiter=';', quotechar='"')
        for row in csv_reader:
            # new key definitions
            if row[0][0] == '/':
                keys = ['time']
                for i in range(1, len(row) - 1):
                    if i % 2 == 0:
                        continue
                    key = row[i]
                    value = float(row[i + 1])
                    keys.append(key)
                    if key not in multipliers:
                        dataset = {
                            'name': key,
                            'data': '',
                            'list': [],
                            'color': _color_(key)
                        }
                        datasets[key] = dataset
                    multipliers[key] = value
            else:
                for i in range(len(row) - 1):
                    key = keys[i]
                    if i > 0:
                        export_multiplier = -1.0 if 'export' in key.lower() else 1.0
                        val = float(row[i]) * multiplier * export_multiplier  # * multipliers[key]
                        scaled_data_point = str(val) if val != 0 or not remove_zeros else ''
                        if quarterly:
                            grouped_datapoints[key] += val / group
                    else:
                        scaled_data_point = row[i]
                        if quarterly:
                            grouped_datapoints[key] = scaled_data_point
                    if quarterly:
                        if int(row[0][-2:]) % group == 0:
                            datasets[key]['list'].append(str(grouped_datapoints[key]))
                            if i == len(row) - 2:
                                grouped_datapoints = defaultdict(float)
                    else:
                        datasets[key]['list'].append(scaled_data_point)
    for key in datasets:
        datasets[key]['data'] = ', '.join(datasets[key]['list'])
    return [datasets['time']] + [v for k, v in datasets.items() if k.lower() in acceptable_keys]


def chart(request, filename, group=1):
    group = int(group)
    if 60 % group != 0:
        return HttpResponseNotFound('<h2 style="font-family:\'Courier New\'"><center>Invalid group parameter')
    filename = '%s.CSV' % filename
    _cache_file_(filename)
    available_days = sorted([f[:-4] for f in os.listdir('.') if f[:2] == '05' and f[-4:] == '.CSV'])
    if not os.path.exists(filename):
        # todo make a proper 404 page
        return HttpResponseNotFound('<h2 style="font-family:\'Courier New\'"><center>No log found for this day')
    datasets = _load_data_(filename, multiplier=1, quarterly=True, group=group)
    context = {
        'labels': datasets[0]['list'],
        'datasets': datasets[1:],
        'days': available_days,
        'today': filename[:-4],
        'group': group,
        'groups': [1, 2, 3, 5, 10, 15, 30, 60]
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
    return render(request, 'charts/demo.html', context)


def csv_based_demo_json(request, solar_max=15000):
    _, datasets = _simple_csv_loader_(['solar', 'grid', 'consumption', 'diesel'], 1, 3, int(solar_max))
    return JsonResponse({dataset['name']: dataset for dataset in datasets})
