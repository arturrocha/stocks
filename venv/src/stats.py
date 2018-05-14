import datetime
import time
import pymongo
import sys
import requests
from progress.bar import Bar
from resources.alphavantage import get_valid_date, get_quote


client = pymongo.MongoClient('localhost', 27017)
db = client.stocks
collection = [data_ for data_ in db.values.find({})]

db.analised.remove({})

def analise_values():
    stock_list= []
    bar = Bar('Counting stocks', max=len(collection))
    for stock_values in collection:
        try:
            if stock_values['MACD'] > stock_values['MACD_Signal']:
                if float(stock_values['CCI']) <= -100.0:
                    if float(stock_values['RSI']) <= 40:
                        stock_list.append(stock_values['symbol'])
                    else:
                        pass
                else:
                    pass
            else:
                pass
            bar.next()
        except:
            bar.next()
            pass
    bar.finish()

    bar = Bar('Processing', max=len(stock_list))
    for stock in stock_list:
        try:
            intraday = get_quote('TIME_SERIES_INTRADAY', stock, 2)
            rsi = get_quote('RSI', stock, 2)
            cci = get_quote('CCI', stock, 2)
            #macd = get_quote('MACD', stock, 2)
            #Time series
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
            #CCI
            key0 = list(cci['Technical Analysis: CCI'].keys())[0]
            cci0 = cci['Technical Analysis: CCI'][key0]['CCI']
            key1 = list(cci['Technical Analysis: CCI'].keys())[1]
            cci1 = cci['Technical Analysis: CCI'][key1]['CCI']
            key2 = list(cci['Technical Analysis: CCI'].keys())[2]
            cci2 = cci['Technical Analysis: CCI'][key2]['CCI']
            time_now = time.time()
            analised = {'symbol': stock, 
                    'timestamp': time_now, 
                    'cci0': cci0, 
                    'cci1': cci1,
                    'cci2': cci2,
                    'rsi0': rsi0, 
                    'rsi1': rsi1,
                    'value': round(value, 2),
                    'volume': volume,
                    'product': round(value * (volume / 2.5), 2)}
            db.analised.insert(analised)
            bar.next()
        except:
            bar.next()
            pass
    bar.finish()

if __name__ == "__main__":
    analise_values()
