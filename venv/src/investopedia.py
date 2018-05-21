from InvestopediaApi import ita
from resources.stocks_config import *
from resources.alphavantage import get_valid_date, get_quote
from progress.bar import Bar

def trade_stock(stock='False', volume=0, action='False', value=0):
    client = ita.Account(investopedia_username, investopedia_password)
    if action == 'sell':
        client.trade(stock, ita.Action.sell, volume)
    elif action == 'sell_limit':
        client.trade(stock, ita.Action.sell, volume, "Limit", value)
    elif action == 'sell_stop':
        client.trade(stock, ita.Action.sell, volume, "Stop", value)
    elif action == 'buy':
        client.trade(stock, ita.Action.buy, volume)
    else:
        pass

    open_trades = client.get_open_trades()
    for open_trade in open_trades:
        print(open_trade)

    portfolio = client.get_current_securities()
    bought_securities = portfolio.bought
    for bought in bought_securities:
        print(bought)


print('start')
#get analised info

#trade
trade_stock('AMX', 1000)
now = datetime.utcnow()
now_time = now.time()

# add weekdays
if time(13,55) <= now.time() <= time(19,55):
    print("Market open")
else:
    print('Market closed')

print('end')

#watchdog
while True:
    try:
        bar.finish()
    except:
        pass

    client = ita.Account(investopedia_username, investopedia_password)
    portfolio = client.get_current_securities()
    open_trades = client.get_open_trades()


    status = client.get_portfolio_status()
    print('Account info')
    print('Value = ${}'.format(status.account_val))
    print('Buy power = ${}'.format(status.buying_power))
    print('Cash = ${}'.format(status.cash))
    money_val = (status.buying_power + status.cash) / 2
    print('BP val = ${}'.format(money_val))
    print('Annual Return = {}%'.format(status.annual_return))
    print('END Info')

    bought_securities = portfolio.bought
    shorted_securities = portfolio.shorted
    options = portfolio.options

    bar = Bar('Processing', max=len(bought_securities))
    for bought in bought_securities:
        stock = bought.symbol
        print(stock)
        for open_trade in open_trades:
            if open_trade.symbol == bought.symbol:
                print(open_trade)
                #print(open_trade.date_time)
                print(open_trade.description)
                #print(open_trade.symbol)
                print(open_trade.quantity)
            else:
                pass

        #print(bought.description)
        b = bought.purchase_price
        print(b)
        q = ita.get_quote(bought.symbol)
        print(q)
        ratio = (1 - (q / b)) * -1
        ratio = round(ratio, 4)
        print('G/L = {}%'.format(round(ratio * 100, 2)))
        print(round(ratio * q * open_trade.quantity, 2))
        try:
            intraday = get_quote('TIME_SERIES_INTRADAY', stock, 2)
            rsi = get_quote('RSI', stock, 2)
        except:
            print('error 33')
            pass
        try:
            # Time series
            # print(intraday['Time Series (15min)'])
            key = list(intraday['Time Series (15min)'].keys())[0]
            open = float(intraday['Time Series (15min)'][key]['1. open'])
            high = float(intraday['Time Series (15min)'][key]['2. high'])
            low = float(intraday['Time Series (15min)'][key]['3. low'])
            close = float(intraday['Time Series (15min)'][key]['4. close'])
            value = (open + high + low + close) / 4
            volume = float(float(intraday['Time Series (15min)'][key]['5. volume']) * 0.1)
            # RSI
            key0 = list(rsi['Technical Analysis: RSI'].keys())[0]
            rsi0 = float(rsi['Technical Analysis: RSI'][key0]['RSI'])
            key1 = list(rsi['Technical Analysis: RSI'].keys())[1]
            rsi1 = float(rsi['Technical Analysis: RSI'][key1]['RSI'])
        except:
            print('error 34')
            pass

        try:
            print('volume = {}'.format(volume))
        except:
            pass

        bar.next()

    #remove this for infinite loop
    break


#open_trades = client.get_open_trades()

#for open_trade in open_trades:
#    print(open_trade.date_time)
#    print(open_trade.description)
#    print(open_trade.symbol)
#    print(open_trade.quantity)
#    #print(ita.get_quote(open_trade.symbol))
