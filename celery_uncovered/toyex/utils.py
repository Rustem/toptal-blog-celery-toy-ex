import os
from os.path import isfile, join
import csv
from time import mktime
from datetime import datetime


def make_csv(filename, lines):
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    with open(filename, 'wb') as csvfile:
        trending_csv = csv.writer(csvfile)
        for line in lines:
            trending_csv.writerow(line)
    return filename

def list_files(folder):
    err_files = [(folder, f) for f in os.listdir(folder) if isfile(join(folder, f))]
    return err_files

def interval_timestamp(interval, t=None):
    if t is None:
        t = ts()
    return t - (t % interval)


def ts():
    return int(mktime(datetime.utcnow().timetuple()))


