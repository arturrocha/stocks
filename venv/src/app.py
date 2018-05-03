# U2ODY5RRZ9315QET
import requests
import datetime
import time
import pymongo
from progress.bar import Bar
import sys

# time settings
start = time.time()
today = datetime.datetime.now()
today = today.strftime("%Y-%m-%d")
yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
yesterday = yesterday.strftime("%Y-%m-%d")
weekday = datetime.datetime.today().weekday()
# mongodb
client = pymongo.MongoClient('localhost', 27017)
db = client.stocks
db.requests.update({'id': 1}, {'status': 'stopped', 'id': 1, 'timestamp': start}, upsert=True)
time.sleep(0.2)
# counters
count = 0
api_key_code = 1

def valid_date():
    # used to determine the proper latest valid date for quotes on alpha vantage
    global today
    global yesterday
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


def get_quote(func, symbol):
    # function to request quote info from alpha vantage
    global api_key_code
    site = 'https://www.alphavantage.co/query?'
    if func is 'TIME_SERIES_DAILY':
        middle = ''
    elif func is 'RSI':
        middle = 'interval=daily&time_period=14&series_type=close'
    elif func is 'MACD':
        middle = 'interval=daily&series_type=close&fastperiod=10'
    elif func is 'CCI':
        middle = 'interval=daily&time_period=20'
    else:
        middle = ''
    if api_key_code == 1:
        api_key = 'U2ODY5RRZ9315QET'
        api_key_code = 2
    elif api_key_code == 2:
        #api_key = 'GQTYHDDNWW6MQOLH'
        api_key = 'U2ODY5RRZ9315QET'
        api_key_code = 1
    # requests control
    request_status = [info for info in db.requests.find({'id': 1})][0]
    time_last = request_status['timestamp']
    time_now = time.time()
    time_diff = time_now - time_last
    #print(request_status['status'])
    #time.sleep(1)
    if time_diff < 1:
        slt = 1.1 - time_diff
        time.sleep(slt)
        #print(time_diff, slt)
    while request_status['status'] == 'running':
        #print(request_status)
        time.sleep(0.2)
        request_status = [info for info in db.requests.find({'id': 1})][0]
    time_now = time.time()
    db.requests.update({'id': 1}, {'status': 'running', 'id': 1, 'timestamp': time_now}, upsert=True)
    result = requests.get('{0}function={1}&symbol={2}&{3}&apikey={4}'.format(site, func, symbol, middle, api_key))
    time_now = time.time()
    db.requests.update({'id': 1}, {'status': 'stopped', 'id': 1, 'timestamp': time_now}, upsert=True)
    # print(result.json())
    try:
        return result.json()
    except:
        return False


list_ = []
with open('stocks.txt') as f:
    for line in f:
        list_.append(line.partition('\t')[0])


while True:
    bar = Bar('Processing', max=len(list_))
    valid_date = valid_date()
    data = {}
    for stock in list_:
        data['symbol'] = stock
        #print(stock)
        try:
            stock_info = [data_ for data_ in db.values.find({'symbol': stock})][0]
            last_valid_date = stock_info['valid_date']
            stock_info_size = len(stock_info)
        except Exception as e:
            last_valid_date = False
            stock_info_size = 1
            #print('update stock info, error = {}'.format(e))
        if stock_info_size < 7:
            last_valid_date = False
        # request control
        if last_valid_date == valid_date:
            #print('{}, skip {}'.format(len(list) - count, stock))
            bar.next()
            pass
        else:
            data['query_date'] = today
            data['valid_date'] = valid_date
            rsi = get_quote('RSI', stock)
            try:
                #print(rsi)
                data['RSI'] = rsi['Technical Analysis: RSI'][valid_date]['RSI']
            except Exception as e:
                # print('rsi {}'.format(rsi))
                # print(e)
                data['RSI'] = '9999'
                pass
            #print(data['RSI'])
            #skipping in case of bad metrics
            if float(data['RSI']) > 30:
                data['CCI'] = 'skipping'
                data['MACD_Signal'] = 'skipping'
                data['MACD_Hist'] = 'skipping'
                data['MACD'] = 'skipping'
                db.values.update({'symbol': stock}, data, upsert=True)
                bar.next()
                continue
            try:
                var = get_quote('CCI', stock)
                data['CCI'] = var['Technical Analysis: CCI'][valid_date]['CCI']
            except Exception as e:
                # print('cci')
                # print(e)
                pass
            try:
                var = get_quote('MACD', stock)
                data['MACD_Hist'] = var['Technical Analysis: MACD'][valid_date]['MACD_Hist']
                data['MACD_Signal'] = var['Technical Analysis: MACD'][valid_date]['MACD_Signal']
                data['MACD'] = var['Technical Analysis: MACD'][valid_date]['MACD']
            except Exception as e:
                #print('macd')
            	#print(e)
                pass
            #print(len(list) - count, data)
            db.values.update({'symbol': stock}, data, upsert=True)
            count += 1
    bar.finish()
	
    end = time.time()
    total_run = end - start
    print('total run = {}'.format(total_run))
    print('avg = {}'.format((total_run / count) / 3))
    print(end)
    time.sleep(60*60)

