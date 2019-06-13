import csv
import json
import os.path

from collections import defaultdict

from django.conf import settings

from ftplib import FTP


def cache_file(filename, hard_reload=True):
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


def load_data(filename, quarterly=True, multiplier=60, remove_zeros=False, acceptable_keys=None, group=1):
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
                        val = float(row[i]) * multiplier  # * multipliers[key]
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


def _generate_new_dataset_(datasets, name='Total', query='i1 + i3', color='blue'):
    dataset = {
        'name': name,
        'data': '',
        'list': [],
        'color': color
    }
    for var_index in range(1, 20):
        query = query.replace('i%d' % var_index, 'float(datasets[%d]["list"][i])' % var_index)
    for i in range(len(datasets[0]['list'])):
        new_value = eval(query)
        dataset['list'].append(str(new_value))
    dataset['data'] = ', '.join(dataset['list'])
    datasets.append(dataset)
    return datasets


# query is of the following form:
# Total|blue = i1 + i3
def generate_new_datasets(datasets, queries):
    for query in queries:
        name_color, query_statement = query.split('=')
        name, color = name_color.strip().split('|')
        datasets = _generate_new_dataset_(datasets, name=name.strip(), color=color, query=query_statement)
    return datasets


def relable_datasets(datasets):
    for i in range(1, len(datasets)):
        datasets[i]['name'] = 'i%d: %s' % (i, datasets[i]['name'])
    return datasets


def group_datasets(datasets, by=2):
    if len(datasets) == 0:
        return datasets
    # deal with time
    datasets[0]['list'] = [datasets[0]['list'][i] for i in range(len(datasets[0]['list'])) if (i + 1) % by == 0]
    datasets[0]['data'] = ', '.join(datasets[0]['list'])
    # deal with the rest
    for index in range(1, len(datasets)):
        grouped_list = list()
        group = list()
        for i in range(len(datasets[index]['list'])):
            group.append(float(datasets[index]['list'][i]))
            if (i + 1) % by == 0:
                value = sum(group) / len(group)
                grouped_list.append(str(value))
                group = list()
        datasets[index]['list'] = grouped_list
        datasets[index]['data'] = ', '.join(datasets[index]['list'])
    return datasets


def load_solar_data(labels, solar_max=1000):
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


def _str_(number):
    if number == 0:
        return ''
    return str(number)


def simple_csv_loader(columns, solar_index, consumption_index, solar_max=15000):
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


def date_scroll_generator(dates, cursor):
    index = dates.index(cursor)
    lower_limit = max(0, index - 2)
    upper_limit = min(len(dates), index + 2) + 1
    previous = dates[index - 1] if index > 0 else None
    next_one = dates[index + 1] if index < len(dates) - 1 else None
    return dates[lower_limit:upper_limit], previous, next_one
