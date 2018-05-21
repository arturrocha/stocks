from datetime import datetime, time
# trade starts at 13:30 utc
now = datetime.utcnow()
now_time = now.time()


if time(13,55) <= now.time() <= time(19,55):
    print("yes, within the interval")
else:
    print('nono')