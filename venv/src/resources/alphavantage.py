import datetime
from resources.stocks_config import *
import pymongo
import time
import requests


client = pymongo.MongoClient('localhost', 27017)
db = client.stocks

def queue_jobs():
    # requests control
    request_status = [info for info in db.requests.find({'id': 1})][0]
    print(request_status)
    pass


def get_quote(func, symbol, priority=1):
    #queue_jobs()
    # function to request quote info from alpha vantage
    global av_api_key
    site = 'https://www.alphavantage.co/query?'
    if func is 'TIME_SERIES_DAILY':
        middle = ''
    elif func is 'RSI':
        middle = 'interval=daily&time_period=14&series_type=close'
    elif func is 'MACD':
        middle = 'interval=daily&series_type=close&fastperiod=10'
    elif func is 'CCI':
        middle = 'interval=daily&time_period=20'
    elif func is 'TIME_SERIES_INTRADAY':
        middle = 'interval=15min'
    else:
        middle = ''
    # requests control
    request_status = [info for info in db.requests.find({'id': 1})][0]
    time_last = request_status['timestamp']
    time_now = time.time()
    time_diff = time_now - time_last
    #print(request_status['status'])
    #time.sleep(1)
    try:
        if priority == 1:
            if request_status['priority'] > 1:
                time.sleep(2)
            else:
                pass
    except:
        pass

    if time_diff < 1:
        slt = 1.1 - time_diff
        time.sleep(slt)
        #print(time_diff, slt)
    while request_status['status'] == 'running':
        #print(request_status)
        time.sleep(0.2)
        request_status = [info for info in db.requests.find({'id': 1})][0]
    time_now = time.time()
    db.requests.update({'id': 1}, {'status': 'running', 'id': 1, 'timestamp': time_now, 'priority': priority}, upsert=True)
    try:
        result = requests.get('{0}function={1}&symbol={2}&{3}&apikey={4}'.format(site, func, symbol, middle, av_api_key))
    except:
        pass
    time_now = time.time()
    db.requests.update({'id': 1}, {'status': 'stopped', 'id': 1, 'timestamp': time_now}, upsert=True)
    # print(result.json())
    try:
        return result.json()
    except:
        return False


def get_valid_date():
    # used to determine the proper latest valid date for quotes on alpha vantage
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    try:
        var = get_quote('RSI', 'A')
        data = var['Technical Analysis: RSI'][today]['RSI']
        valid_date = today
    except KeyError:
        valid_date = yesterday

    if valid_date == yesterday:
        wday = datetime.datetime.today().weekday()
        if wday == 0:
            friday = datetime.datetime.now() - datetime.timedelta(days=3)
            friday = friday.strftime("%Y-%m-%d")
            valid_date = friday
        if wday == 7:
            friday = datetime.datetime.now() - datetime.timedelta(days=2)
            friday = friday.strftime("%Y-%m-%d")
            valid_date = friday
    #print('today not ready, using {}'.format(valid_date))
    return valid_date


