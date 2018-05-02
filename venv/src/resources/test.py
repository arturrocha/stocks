import pyprind
import sys
import time

n = 20
bar = pyprind.ProgBar(n, stream=sys.stdout)
for i in range(n):
    time.sleep(1)
    if i is 10:
        continue
    print('i,{}'.format(i))
    bar.update()
