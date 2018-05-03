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
    #print(request_status['status'])
    time.sleep(1)
    if time_diff < 1:
        slt = 1.1 - time_diff
        time.sleep(slt)
        #print(time_diff, slt)
    while request_status['status'] == 'running':
        #print(request_status)
        time.sleep(1)
        request_status = [info for info in db.requests.find({'id': 1})][0]
    time_now = time.time()
    db.requests.update({'id': 1}, {'status': 'running', 'id': 1, 'timestamp': time_now}, upsert=True)
    link = '{0}function={1}&symbol={2}&{3}&apikey={4}'.format(site, func, symbol, middle, api_key)
    #print(link)
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
    try:
        intraday = get_quote('TIME_SERIES_INTRADAY', stock)
        time.sleep(1)
    except:
        pass

    rsi = get_quote('RSI', stock)
    #time.sleep(1)
    #cci = get_quote('CCI', stock)
    #time.sleep(1)
    #macd = get_quote('MACD', stock)
    #time.sleep(1)
    try:
        #Time series
        #print(intraday['Time Series (15min)'])
        key = list(intraday['Time Series (15min)'].keys())[0]
        open = float(intraday['Time Series (15min)'][key]['1. open'])
        high = float(intraday['Time Series (15min)'][key]['2. high'])
        low = float(intraday['Time Series (15min)'][key]['3. low'])
        close = float(intraday['Time Series (15min)'][key]['4. close'])
        value = (open + high + low + close) / 4
        volume = float(float(intraday['Time Series (15min)'][key]['5. volume']) * 0.1)
        #RSI
        key0 = list(rsi['Technical Analysis: RSI'].keys())[0]
        rsi0 = float(rsi['Technical Analysis: RSI'][key0]['RSI'])
        key1 = list(rsi['Technical Analysis: RSI'].keys())[1]
        rsi1 = float(rsi['Technical Analysis: RSI'][key1]['RSI'])
        if rsi0 < 30:
            print('stock={}, value avg={}, volume10%={}, product={}, RSI={}'.format(stock,
                                                                                    round(value, 2),
                                                                                    volume,
                                                                                    round(value * (volume / 2.5), 2),
                                                                                    rsi0))

            if rsi0 < rsi1:
                print('felled')
            else:
                print('increasing')

        # resume
    except:
        print('fail')
        pass