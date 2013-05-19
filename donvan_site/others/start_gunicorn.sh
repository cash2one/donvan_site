#!/bin/bash
gunicorn_django -D -c others/gunicorn.conf.py

