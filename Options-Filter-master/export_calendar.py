import finance_options
import os

if __name__ == '__main__':
    a = finance_options.FinanceOptions(['AAPL', 'AA'])
    a.dataframe.to_excel('financeopts.xlsx', sheet_name='Sheet1')
    dir_name = os.path.dirname(os.path.abspath(__file__))
    absolute_path = os.path.join(dir_name, 'financeopts.xlsx')
    os.startfile(absolute_path)
