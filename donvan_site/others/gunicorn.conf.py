import os

PATH = os.path.dirname(os.path.realpath(__file__))

bind = "127.0.0.1:8000"
# logfile = "%s/gunicorn.log"%PATH
logfile = '/var/log/gunicorn.log'
workers = 3
