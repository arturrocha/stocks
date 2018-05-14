import datetime

today = datetime.datetime.now()

print(today)

today = today.strftime("%Y-%m-%d")

print(today)

yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

print(yesterday)
