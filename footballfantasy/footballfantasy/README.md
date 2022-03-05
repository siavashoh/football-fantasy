#### How to install require packages

```bash
python3.8 -m pip install -r requirements.txt
```

#### How to migrate database after install requirements

```bash
python manage.py makemigrations
python manage.py migrate
```

#### Inside `/footballfantasy/settings.py` file you can:

1. Set `DATABASES` configurations.
2. Set `EMAIL` configurations.
3. Set `ALLOW_HOSTS`.
4. Set `DEBUG` to `false`.