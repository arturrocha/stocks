import datetime
import time
import pymongo
import sys
import requests


client = pymongo.MongoClient('localhost', 27017)
db = client.stocks
collection = [data_ for data_ in db.values.find({})]

def get_quote(func, symbol):
    # function to request quote info from alpha vantage
    site = 'https://www.alphavantage.co/query?'
    if func is 'TIME_SERIES_DAILY':
        middle = ''
    elif func is 'RSI':
        middle = 'interval=15min&time_period=14&series_type=close'
    elif func is 'MACD':
        middle = 'interval=15min&series_type=close&fastperiod=10'
    elif func is 'CCI':
        middle = 'interval=15min&time_period=20'
    elif func is 'TIME_SERIES_INTRADAY':
        middle = 'interval=15min'
    else:
        middle = ''
    api_key = 'U2ODY5RRZ9315QET'

    # requests control
    request_status = [info for info in db.requests.find({'id': 1})][0]
    time_last = request_status['timestamp']
    time_now = time.time()
    time_diff = time_now - time_last
    print(request_status['status'])
    time.sleep(1)
    if time_diff < 1:
        slt = 1.1 - time_diff
        time.sleep(slt)
        print(time_diff, slt)
    while request_status['status'] == 'running':
        print(request_status)
        time.sleep(1)
        request_status = [info for info in db.requests.find({'id': 1})][0]
    time_now = time.time()
    db.requests.update({'id': 1}, {'status': 'running', 'id': 1, 'timestamp': time_now}, upsert=True)
    result = requests.get('{0}function={1}&symbol={2}&{3}&apikey={4}'.format(site, func, symbol, middle, api_key))
    time_now = time.time()
    db.requests.update({'id': 1}, {'status': 'stopped', 'id': 1, 'timestamp': time_now}, upsert=True)
    # print(result.json())
    return result.json()

stock_list= []
count = 0
for stock_values in collection:
    try:
        stock_values['MACD']
        stock_values['CCI']
        stock_values['RSI']
    except:
        continue
    if stock_values['MACD'] > stock_values['MACD_Signal']:
        if float(stock_values['CCI']) <= -100.0:
            if float(stock_values['RSI']) <= 30:
                stock_list.append(stock_values['symbol'])
                #url = 'https://www.tradingview.com/chart/?symbol={}'.format(stock_values['symbol'])
                #print(url)
                #print(stock_values)
                count += 1

for stock in stock_list:
    print(stock)
    var = get_quote('TIME_SERIES_INTRADAY', stock)
    print(var)
    break

