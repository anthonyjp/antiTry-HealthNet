:: Install Requirements First, either for the system or for the user
:: Runserver insecurely (to serve static files) and do not reload if a file is edited
:: Collect Any Uncollected Static Files, clearing the stale files
:: Attempt to make migrations and then migrate. If python is a link to python2 then this will fail, an explicit python3 case is included
(pip install -r requirements.txt || pip install -r requirements.txt --user) && <nul ^
 (python manage.py makemigrations --noinput || python3 manage.py makemigrations --noinput --merge) && <nul ^
 (python manage.py migrate || python3 manage.py migrate) && <nul ^
 python manage.py createhnsuperuser --noinput --email admin@admin.com --username Admin || <nul ^
 python manage.py runserver 8000 --insecure --noreload
