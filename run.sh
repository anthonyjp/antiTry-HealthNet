#!/usr/bin/env bash

command -v pip >/dev/null 2>&1 || { echo >&2 "I require pip but it's not installed.  Aborting."; exit 1; }
command -v python >/dev/null 2>&1 || { echo >&2 "I require python but it's not installed.  Aborting."; exit 1; }

ret=`python -c 'import sys; print("%i" % (sys.hexversion<0x03000000))'`
if [ $ret -eq 0 ]; then
    pycmd='python3'
    echo "Python does not default to Python 3, attempting to use python3 explicitly."
else
    pycmd='python'
fi

pip install -r requirements.txt || pip install -r requirements.txt --user && \
"$pycmd" manage.py makemigration --noinput --merge && "$pycmd" manage.py migrate && \
"$pycmd" manage.py collectstatic --noinput -v 0 && "$pycmd" manage.py runserver 8000 --insecure --noreload