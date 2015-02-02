__author__ = 'sagonzal'
from password import *
import psycopg2

try:
    pgconn = psycopg2.connect (host=pghost, database=pguser ,user=pguser, password=pgpassword)
    pgcursor = pgconn.cursor()
except Exception as e:
    print e
    pass




