import threading
import os
import sys
from datetime import datetime
import time
import logging
import subprocess
import sqlite3
import geocoder

now=datetime.now()
conn = sqlite3.connect('test.db', check_same_thread=False)
cur = conn.cursor()
path = 'rootDir'
path2 = '2018'
sql = 'SELECT path from Camera1'
cur.execute(sql)
get=cur.fetchone()
print(str(get))
ha = 'Qmaye41t4c4APWSTHtW6c7fyGSrDdnR9svWSHtEdeVmNAn'
cur.execute("""UPDATE Camera1 SET hash=? WHERE path=?""", (str(ha), str(get[0])))
conn.commit()
query = 'SELECT * FROM Camera1'
cur.execute(query)
get = cur.fetchall()
print(get)

year=str(now.year)
month=str(now.month)

sql = 'SELECT hash FROM Camera1 WHERE path=?'
month_path=('rootDir/'+str(now.year)+'/'+str(now.month),)
year_path=('rootDir/'+str(now.year),)
cur.execute(sql, month_path)
print(str(cur.fetchone()[0]))
cur.execute(sql, year_path)
print(str(cur.fetchone()[0]))

ha='QmUNLLsPACCz1vLxQVkXqqLX5R1X345qqfHbsf67hvA3Nn'
sql = 'UPDATE Camera1 SET hash=? WHERE path=?'
update=(str(ha), 'rootDir/'+str(year)+'/'+str(month))
cur.execute(sql, update)
conn.commit()
sql = 'SELECT * FROM Camera1'
cur.execute(sql)
get = cur.fetchall()
print(get)

print('year : {}, month : {}'.format(year,month))
