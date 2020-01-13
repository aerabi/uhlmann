# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os.path

from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import render


from .service import cache_file
from .service import load_data
from .service import generate_new_datasets
from .service import load_solar_data
from .service import simple_csv_loader
from .service import group_datasets
from .service import date_scroll_generator
from .service import relable_datasets


def chart(request, filename, group=1, queries=None):
    group = int(group)
    if 60 % group != 0:
        return HttpResponseNotFound('<h2 style="font-family:\'Courier New\'"><center>Invalid group parameter')
    filename = '%s.CSV' % filename
    cache_file(filename)
    months = ['%02d' % i for i in range(1, 13)]
    available_days = sorted([f[:-4] for f in os.listdir('.') if f[-4:] == '.CSV' and f[:2] in months])
    today = filename[:-4]
    days, prev_day, next_day = date_scroll_generator(available_days, today)
    if not os.path.exists(filename):
        # todo make a proper 404 page
        return HttpResponseNotFound('<h2 style="font-family:\'Courier New\'"><center>No log found for this day')
    datasets = load_data(filename, multiplier=1, quarterly=False, group=1)
    if group != 1:
        datasets = group_datasets(datasets, by=group)
    if queries is not None:
        datasets = generate_new_datasets(datasets, queries.split(';'))
    datasets = relable_datasets(datasets)
    context = {
        'labels': datasets[0]['list'],
        'datasets': datasets[1:],
        'days': days,
        'today': today,
        'prev_day': prev_day,
        'next_day': next_day,
        'group': group,
        'groups': [1, 2, 3, 5, 10, 15, 30, 60],
        'formulae': queries.replace(';', ';\n') if queries is not None else None
    }
    return render(request, 'charts/chart.html', context)


def get_data(request, filename, group=1, queries=None):
    group = int(group)
    if 60 % group != 0:
        return JsonResponse({'message': 'group must divide 60'}, status=400)
    filename = '%s.CSV' % filename
    cache_file(filename)
    if not os.path.exists(filename):
        return JsonResponse({'message': 'day not found'}, status=404)
    datasets = load_data(filename, multiplier=1, quarterly=False, group=1)
    if group != 1:
        datasets = group_datasets(datasets, by=group)
    if queries is not None:
        datasets = generate_new_datasets(datasets, queries.split(';'))
    datasets = relable_datasets(datasets)
    return JsonResponse(datasets, safe=False)


def demo(request, solar_max=1000):
    all_datasets = load_data('0225.CSV', quarterly=True)
    labels = all_datasets[0]['list']
    consumption_dataset = all_datasets[2]
    solar_dataset = load_solar_data(labels, int(solar_max))
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


def csv_based_demo(request, solar_max=15000):
    labels, datasets = simple_csv_loader(['solar', 'grid', 'consumption', 'diesel'], 1, 3, int(solar_max))
    context = {
        'labels': labels,
        'datasets': datasets,
    }
    return render(request, 'charts/demo.html', context)


def csv_based_demo_json(request, solar_max=15000):
    _, datasets = simple_csv_loader(['solar', 'grid', 'consumption', 'diesel'], 1, 3, int(solar_max))
    return JsonResponse({dataset['name']: dataset for dataset in datasets})
