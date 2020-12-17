# Uhlmann
Web Project for Uhlmann Solarelectronic GmbH

## Install on VPS

The following setup instructions are based on Ubuntu 20.04 and the `root` user, hence no `sudo` is written.

### Install OS Packages

DigitalOcean droplets of Ubuntu 20.04 come with `git`, `vim`, and `python3.8`, so we won't install them separately.
Make sure the other required packages are installed on the OS level:

```bash
apt update
apt install python3-pip
pip3 install virtualenv
```

### Clone the Code

Clone the project from GitHub:

```bash
git clone https://github.com/aerabi/uhlmann.git
cd uhlmann
```

### Install Python Packages

Create a virtual environment for the Python packages, and install them:

```bash
virtualenv -p python3.8 venv
source venv/bin/activate
cd arno
pip install -r requirements.txt
```

### Initialize Django

To run the Django app, one needs to do the migrations and collect static:

```bash
python manage.py migrate
python manage.py collectstatic
```

### Add the Current Host to `ALLOWED_HOSTS`

Edit the settings file and add the current hostname/IP to the allowed hosts:

```bash
vim arno/settings.py
```

And then add the hosts to the variable `ALLOWED_HOSTS`:

```python
ALLOWED_HOSTS = [
    '46.101.251.251',
    'server',
    'arno',
    '167.71.40.77',
    'localhost',
    'arno-chart.appspot.com',
]
```

(Use another editor if you're not familiar with `vim`.)

### Run the Server with NoHup

Run the server on IP `0.0.0.0` and port `80`:

```bash
nohup python manage.py runserver 0.0.0.0:80 &
```

Then the Django app is running on the VPS, e.g. on [167.71.40.77/chart](http://167.71.40.77/chart).

## Install

The root directory project is `arno` (one level deeper than
repository's root). The working directory for all the commands below
are `arno`:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
```

## Deploy to Google Cloud

Put build files of the Angular project under
`/static/solar-chart/`. Then:
```bash
gcloud app deploy app.yaml --project=arno-chart
```
