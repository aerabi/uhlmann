import json
import os

from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.
def ftp_form(request):
    return render(request, 'forms/ftp_form.html')


def ftp_form_submit(request):
    url = request.POST.get('url', '')
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    # save to file
    data = {'url': url, 'username': username, 'password': password}
    with open('ftp_setting.json', 'w') as output_file:
        json.dump(data, output_file)
    delete_old_csv_files()
    return HttpResponse('<center><p style="font-size:x-large"><br><br><br><br>'
                        'The new data has been successfully recorded')


def delete_old_csv_files():
    folder_path = '.'
    for f in os.listdir(folder_path):
        if '.csv' in f.lower():
            os.remove(os.path.join(folder_path, f))
