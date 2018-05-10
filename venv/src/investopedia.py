from InvestopediaApi import ita
from resources.config import *


client = ita.Account(investopedia_username, investopedia_password)

status = client.get_portfolio_status()

print(status.account_val)
print(status.buying_power)
print(status.cash)
print(status.annual_return)


portfolio = client.get_current_securities()

bought_securities = portfolio.bought
shorted_securities = portfolio.shorted
options = portfolio.options

for bought in bought_securities:
    print(bought.symbol)
    print(bought.description)
    print(bought.purchase_price)
    # etc.

# Repeat above loop for shorted securities and options

open_trades = client.get_open_trades()

for open_trade in open_trades:
    print(open_trade.date_time)
    print(open_trade.description)
    print(open_trade.symbol)
    print(open_trade.quantity)

print(ita.get_quote("ABEV"))

