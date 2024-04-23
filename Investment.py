from StockAccount import StockAccount

import pandas as pd
import datetime

class Investment():

    def __init__(self, file_name, ticker) -> None:

        self.file_name = file_name
        
        self.file_name.index = pd.to_datetime(self.file_name.index, format="%Y-%m-%d")

        self.ticker = ticker
        
        self.stockAccount = StockAccount()


    def inside_candle_strategy():
        pass


    def exponential_moving_average(self, length, column):
       
        ema = self.file_name['close'].ewm(span=length, adjust=False).mean().rename(column)

        return ema
    
    
    def daily_ema_cross_over(self, length_1, length_2, end_date='2018-12-31') -> None:
        
        ema_1_col = str(length_1) + '_EMA'
        ema_2_col = str(length_2) + '_EMA'

        ema_1 = self.exponential_moving_average(length=length_1, column=ema_1_col)
        ema_2 = self.exponential_moving_average(length=length_2, column=ema_2_col)

        self.file_name = pd.concat([self.file_name, ema_1, ema_2], axis=1)

        # self.file_name.set_index("date", inplace = True) # Edit later
        # self.file_name.index = pd.to_datetime(self.file_name.index, format="%Y-%m-%d") # Edit later

        cur_date = self.file_name.index[0]
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

        
        while cur_date != end_date:

            self.stockAccount.execute_limit_order(cur_date=cur_date)

            if self.file_name.loc[cur_date, ema_1_col] > self.file_name.loc[cur_date, ema_2_col] and len(self.stockAccount._portfolios) == 0:

                price = self.file_name.loc[cur_date + datetime.timedelta(days=1), 'open']

                # print(f'date: {cur_date}, buy: True, ema1: {self.file_name.loc[cur_date, ema_1]}, ema2: {self.file_name.loc[cur_date, ema_2]}, price: {price}')
                
                self.stockAccount.send_limit_buy_order(ticker=self.ticker, date=cur_date + datetime.timedelta(days=1), price=price, ls=True)

            if self.file_name.loc[cur_date, ema_1_col] < self.file_name.loc[cur_date, ema_2_col] and len(self.stockAccount._portfolios) == 1:

                price = self.file_name.loc[cur_date + datetime.timedelta(days=1), 'open']

                # print(f'date: {cur_date}, buy: False, ema1: {self.file_name.loc[cur_date, ema_1]}, ema2: {self.file_name.loc[cur_date, ema_2]}, price: {price}')

                self.stockAccount.send_limit_sell_order(ticker=self.ticker, date=cur_date + datetime.timedelta(days=1), price=price, ls=True)

            cur_date += datetime.timedelta(days=1)




    


