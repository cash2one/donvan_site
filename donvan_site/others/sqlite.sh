#!/bin/bash
rm sqlite.db
python manage.py syncdb
