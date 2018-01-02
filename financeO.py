import json
from datetime import datetime
import urllib.request

BASE_URL = 'https://query2.finance.yahoo.com/v7/finance/options/'


class FinanceOption:
    __ticker = ''
    __jsonInfo = {}
    __currentMarketPrice = 0
    __closestStrikes = []
    __closestPuts = []
    __expirationDate = 0

    def __init__(self, symbol):

        # sets up the api for given symbol

        the_url = BASE_URL + symbol + '?'
        content = urllib.request.urlopen(the_url)
        self.__jsonInfo = json.load(content)

        self.__ticker = symbol
        self.__currentMarketPrice = self.find_current_market_price()
        self.__closestStrikes = self.closest_calls_strikes()
        self.__closestPuts = self.closest_put_strikes()
        self.__expirationDate = self.__closestStrikes[0]['expiration']

    def find_current_market_price(self):
        return self.__jsonInfo['optionChain']['result'][0]['quote']['regularMarketPrice']

    def closest_calls_strikes(self):
        all_strikes = self.__jsonInfo['optionChain']['result'][0]['options'][0]['calls']
        # n is the lower option number
        n = 0
        low_strike_option = all_strikes[n]
        # loop iterates through until the next strike is above market price or n is the second to last element
        while (all_strikes[n + 1]['strike'] < self.__currentMarketPrice) and (n + 2 < len(all_strikes)):
            n += 1
            low_strike_option = all_strikes[n]
        high_strike_option = all_strikes[n + 1]
        return [low_strike_option, high_strike_option]

    # I could combine these two methods together but probably doesn't matter.
    def closest_put_strikes(self):
        all_strikes = self.__jsonInfo['optionChain']['result'][0]['options'][0]['puts']
        n = 0
        low_strike_option = all_strikes[n]
        while (all_strikes[n+1]['strike'] < self.__currentMarketPrice):
            n += 1
            low_strike_option = all_strikes[n]
        high_strike_option = all_strikes[n + 1]
        return [low_strike_option, high_strike_option]

    def get_bids(self, num):
        if (num == 0):
            low_bid = self.__closestStrikes[0]['bid']
            high_bid = self.__closestStrikes[1]['bid']
        else:
            low_bid = self.__closestPuts[0]['bid']
            high_bid = self.__closestPuts[0]['bid']
        return [low_bid, high_bid]

    def get_asks(self, num):
        if (num == 0):
            low_ask = self.__closestStrikes[0]['ask']
            high_ask = self.__closestStrikes[1]['ask']
        else:
            low_ask = self.__closestPuts[0]['ask']
            high_ask = self.__closestPuts[1]['ask']
        return [low_ask, high_ask]

    def get_last_prices(self, num):
        if (num == 0):
            low_last_price = self.__closestStrikes[0]['lastPrice']
            high_last_price = self.__closestStrikes[1]['lastPrice']
        else:
            low_last_price = self.__closestPuts[0]['lastPrice']
            high_last_price = self.__closestPuts[1]['lastPrice']
        return [low_last_price, high_last_price]

    def get_closest_strikes(self):
        return self.__closestStrikes

    def get_closest_puts(self):
        return self.__closestPuts

    def get_json(self):
        return self.__jsonInfo

    def get_expiration_date(self):
        return self.__expirationDate

    def get_expiration_weekday(self):
        return datetime.fromtimestamp(self.__expirationDate).strftime('%A')

    def get_current_market_price(self):
        return self.__currentMarketPrice

    def get_ticker(self):
        return self.__ticker
