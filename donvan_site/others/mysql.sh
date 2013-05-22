#!/bin/bash

USER=donvan
PASSWD=qweqwe
SQL='DROP DATABASE donvan_site;
CREATE DATABASE IF NOT EXISTS donvan_site;'
mysql -u$USER -p$PASSWD -e "$SQL"
ipython manage.py syncdb
