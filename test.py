import os
import datetime
import time
def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)
d = modification_date('/Users/leebongho/monitoring/Camera_/a.txt')
print(d)

print("last modified: %s" % time.ctime(os.path.getmtime('/Users/leebongho/monitoring/Camera_/a.txt')))
print("created: %s" % time.ctime(os.path.getctime('/Users/leebongho/monitoring/Camera_/a.txt')))
