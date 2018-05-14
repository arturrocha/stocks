import requests
import datetime
import time
import pymongo
import sys
from progress.bar import Bar
from resources.alphavantage import get_valid_date, get_quote

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

list_ = []
with open('stocks.txt') as f:
    for line in f:
        list_.append(line.partition('\t')[0])

valid_date = False

while True:
    print('start')
    bar = Bar('Processing', max=len(list_))
    valid_date = get_valid_date()
    data = {}
    for stock in list_:
        data['symbol'] = stock
        try:
            stock_info = [data_ for data_ in db.values.find({'symbol': stock})][0]
            last_valid_date = stock_info['valid_date']
            stock_info_size = len(stock_info)
        except Exception as e:
            last_valid_date = False
            stock_info_size = 1
        if stock_info_size < 7:
            last_valid_date = False
        # request control
        if last_valid_date == valid_date:
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
            if float(data['RSI']) > 35:
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
                pass
            db.values.update({'symbol': stock}, data, upsert=True)
    bar.finish()

    end = time.time()
    total_run = end - start
    try:
        print('total run = {}h'.format((total_run / 60) / 60))
        print(end)
    except:
        pass
    print('sleep for 1h')
    valid_date = False
    time.sleep(3600)

