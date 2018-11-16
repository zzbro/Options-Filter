import urllib.request
import pandas as pd
import json
import heapq
import numpy as np

BASE_URL = 'https://query2.finance.yahoo.com/v7/finance/options/'
COLUMNS = ['Stock Symbol', 'Stock Price', 'Call Strike', 'Call Price', 'Call %', 'Put Strike',
           'Put Price', 'Put %', 'Call Expiration Date', 'Put Expiration Date']

def calc_percentages(call_prices, strikes, stock_price):
    percentages = []
    for index, strike in enumerate(strikes):
        percentages.append(round(((strike + call_prices[index] - stock_price) / stock_price), 4)*100)
    return percentages

class FinanceOptions:

    # Pass in a list of company symbols to query
    def __init__(self, tickers, k = 2):
        self.dataframe = self.query_data(tickers, k)
        self.dataframe = self.dataframe[COLUMNS].set_index('Stock Symbol')

    def query_data(self, tickers, k):
        dataframe = []
        for ticker in tickers:
            dataframe.append(self.each_ticker(ticker, k))
        return pd.concat(dataframe)

    def each_ticker(self, ticker, num_closest):
        def binary_search(sorted_list, k, target, key='strike'):
            '''
            :param sorted_list: an iterable to find k closest elements to target
            :param k: number of closest elements
            :param target: target to find
            :return: set of k_closest elements in sorted_list
            '''
            sorted_list = [i[key] for i in sorted_list]
            end = len(sorted_list)
            assert 0 < k < end
            if target <= sorted_list[0]:
                return sorted_list[k:]
            elif target >= sorted_list[-1]:
                return sorted_list[end-k:end]

            low = 0
            high = len(sorted_list)-1
            # distance, index
            closest_distance = abs(target-sorted_list[0])
            closest_index = 0
            while low < high:
                middle = (low+high)//2
                current = sorted_list[middle]
                current_distance = abs(target - current)
                if current < target:
                    low = middle + 1
                elif current > target:
                    high = middle - 1
                else:
                    closest_index = middle
                    closest_distance = 0
                    break
                if current_distance < closest_distance:
                    closest_distance = current
                    closest_index = middle
            if k == 1:
                return sorted_list[closest_index]
            k_closest = []
            counter = 0
            # overshoot in case of edge index
            for index in range(closest_index-k, closest_index+k):
                if index < 0 or index >= end:
                    continue
                if counter != k:
                    heapq.heappush(k_closest, (-1*(target-sorted_list[0]), index))
                    counter += 1
                else:
                    heapq.heappushpop(k_closest, (-1*(target-sorted_list[0]), index))
            k_closest = {sorted_list[elem[1]] for elem in k_closest}
            k_closest = list(k_closest)
            k_closest.sort()
            return k_closest

        query_url = BASE_URL + ticker + '?'
        with urllib.request.urlopen(query_url) as url:
            json_info = json.load(url)
            json_info = json_info['optionChain']['result'][0]
            current_market_price = json_info['quote']['regularMarketPrice']
            all_calls = json_info['options'][0]['calls']
            all_puts = json_info['options'][0]['puts']

            k_closest_calls_strikes = binary_search(all_calls, num_closest, current_market_price)
            k_closest_puts_strikes = binary_search(all_puts, num_closest, current_market_price)
            print(k_closest_calls_strikes, k_closest_puts_strikes, current_market_price)
            k_closest_calls = [call for call in all_calls if call['strike'] in k_closest_calls_strikes]
            k_closest_puts = [put for put in all_puts if put['strike'] in k_closest_puts_strikes]
            k_call_last_prices = [call['lastPrice'] for call in k_closest_calls]
            k_put_last_prices = [put['lastPrice'] for put in k_closest_puts]

            call_expiration_dates = [pd.Timestamp(call['expiration'], unit='s').strftime('%Y-%m-%d %H:%M:%S')
                                     for call in k_closest_calls]
            put_expiration_dates = [pd.Timestamp(put['expiration'], unit='s').strftime('%Y-%m-%d %H:%M:%S')
                                    for put in k_closest_puts]
        row = pd.DataFrame({'Stock Symbol': ticker, 'Stock Price': current_market_price,
               'Call Strike': pd.Series(k_closest_calls_strikes),
               'Call Price': pd.Series(k_call_last_prices),
               'Call %': pd.Series(calc_percentages(k_call_last_prices,
                                                    k_closest_calls_strikes, current_market_price)),
               'Put Strike': pd.Series(k_closest_puts_strikes),
               'Put Price': pd.Series(k_put_last_prices),
               'Put %': pd.Series(calc_percentages(k_put_last_prices, k_closest_puts_strikes, current_market_price)),
               'Call Expiration Date': call_expiration_dates,
               'Put Expiration Date': put_expiration_dates})
        return row
