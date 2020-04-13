# Uhlmann
Web Project for Uhlmann Solarelectronic GmbH

## Install

The root directory project is `arno` (one level deeper than
repository's root). The working directory for all the commands below
are `arno`:

```bash
$ pip install -r requirements.txt
$ python manage.py migrate
$ python manage.py collectstatic
```

## Deploy

Put build files of the Angular project under
`/static/solar-chart/`. Then:
```bash
$ gcloud app deploy app.yaml --project=arno-chart
```

## Development

To connect to DB:
```bash
$ ./cloud_sql_proxy -instances=arno-chart:europe-west3:arno-db=tcp:3306
```
