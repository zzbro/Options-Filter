import csv
import financeO
import time

mySymbol = input('Please enter your company symbol')

aCompanyInfo = financeO.FinanceOption(mySymbol)

rows = {'ticker': mySymbol, 'Current Market Price': aCompanyInfo.get_current_market_price(),
        'closest strikes': aCompanyInfo.get_closest_strikes()}

myStrikes = aCompanyInfo.get_closest_strikes()
myLowStrike = myStrikes[0]
myHighStrike = myStrikes[1]
myPuts = aCompanyInfo.get_closest_puts()
myLowPut = myPuts[0]
myHighPut = myPuts[1]


def calc_percentages(call_price, strike, stock_price):
    return (strike + call_price - stock_price) / stock_price


with open('@1_financeopts.csv', 'w+', newline='') as excel_fil:
    file_writer = csv.writer(excel_fil)
    file_writer.writerow(["Stock Symbol", "Stock Price", "Strike", "Call Price", "Call %", "Put Price", "Put %",
                          "Expiration Date"])
    file_writer.writerow([aCompanyInfo.get_ticker(),
                          aCompanyInfo.get_current_market_price(),
                          myLowStrike['strike'],
                          myLowStrike['lastPrice'],
                          calc_percentages(myLowStrike['lastPrice'], myLowStrike['strike'],
                                           aCompanyInfo.get_current_market_price()),
                          myLowPut['lastPrice'],
                          calc_percentages(myLowPut['lastPrice'], myLowPut['strike'],
                                           aCompanyInfo.get_current_market_price()),
                          time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(aCompanyInfo.get_expiration_date()))])
    file_writer.writerow([None,
                          None,
                          myHighStrike['strike'],
                          myHighStrike['lastPrice'],
                          calc_percentages(myHighStrike['lastPrice'], myHighStrike['strike'],
                                           aCompanyInfo.get_current_market_price()),
                          myHighPut['lastPrice'],
                          calc_percentages(myHighPut['lastPrice'], myHighPut['strike'],
                                           aCompanyInfo.get_current_market_price()),
                          time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(aCompanyInfo.get_expiration_date()))])

