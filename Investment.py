from StockAccount import StockAccount

import pandas as pd
import datetime

class Investment():

    def __init__(self, file_name, ticker) -> None:

        self.file_name = file_name
        
        # self.file_name.index = pd.to_datetime(self.file_name.index, format="%Y-%m-%d")

        self.ticker = ticker
        
        self.stockAccount = StockAccount()


    def exponential_moving_average(self, length, column):
       
        ema = self.file_name['close'].ewm(span=length, adjust=False).mean().rename(column)

        return ema
    
    
    def daily_ema_cross_over(self, length_1, length_2, end_date='2018-12-31') -> None:

        self.file_name.set_index("date", inplace=True)
        self.file_name.index = pd.to_datetime(self.file_name.index, format="%Y-%m-%d")
        
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

            if self.file_name.loc[cur_date, ema_1_col] > self.file_name.loc[cur_date, ema_2_col] and len(self.stockAccount.get_portfolios()) == 0:

                price = self.file_name.loc[cur_date + datetime.timedelta(days=1), 'open']

                # print(f'date: {cur_date}, buy: True, ema1: {self.file_name.loc[cur_date, ema_1]}, ema2: {self.file_name.loc[cur_date, ema_2]}, price: {price}')
                
                self.stockAccount.send_limit_buy_order(ticker=self.ticker, date=cur_date + datetime.timedelta(days=1), price=price, ls=True)

            if self.file_name.loc[cur_date, ema_1_col] < self.file_name.loc[cur_date, ema_2_col] and len(self.stockAccount.get_portfolios()) == 1:

                price = self.file_name.loc[cur_date + datetime.timedelta(days=1), 'open']

                # print(f'date: {cur_date}, buy: False, ema1: {self.file_name.loc[cur_date, ema_1]}, ema2: {self.file_name.loc[cur_date, ema_2]}, price: {price}')

                self.stockAccount.send_limit_sell_order(ticker=self.ticker, date=cur_date + datetime.timedelta(days=1), price=price, ls=True)

            cur_date += datetime.timedelta(days=1)


    def cal_signal(self) -> None:

        self.file_name['max_value'] = None
        self.file_name['min_value'] = None
        self.file_name.loc[0, 'max_value'] = self.file_name['high'].iloc[0]
        self.file_name.loc[0, 'min_value'] = self.file_name['low'].iloc[0]

        self.file_name['signal'] = None
        self.file_name.loc[0, 'signal'] = 0

        # Loop through the DataFrame from the second day onwards

        for i in range(1, len(self.file_name)):
           
            if self.file_name['close'].iloc[i] > self.file_name.loc[i - 1, 'max_value']:
                
                self.file_name.loc[i, 'max_value'] = self.file_name['high'].iloc[i]
                self.file_name.loc[i, 'min_value'] = self.file_name['low'].iloc[i]
                self.file_name.loc[i, 'signal'] = 0
         
            elif self.file_name['close'].iloc[i] < self.file_name.loc[i - 1, 'min_value']:
                
                self.file_name.loc[i, 'max_value'] = self.file_name['high'].iloc[i]
                self.file_name.loc[i, 'min_value'] = self.file_name['low'].iloc[i]
                self.file_name.loc[i, 'signal'] = 0

            else:
                self.file_name.loc[i, 'max_value'] = self.file_name['max_value'].iloc[i - 1]
                self.file_name.loc[i, 'min_value'] = self.file_name['min_value'].iloc[i - 1]
                self.file_name.loc[i, 'signal'] = self.file_name.loc[i - 1, 'signal'] + 1

        self.file_name['signal_diff'] = self.file_name['signal'].diff()
        self.file_name['buyORsell'] = 0

        for index, row in self.file_name.iterrows():

            if row['signal_diff'] <= -3 and row['close'] > self.file_name['max_value'].iloc[index - 1]:
                self.file_name.loc[index, 'buyORsell'] = 1

            elif row['signal_diff'] <= -3 and row['close'] < self.file_name['min_value'].iloc[index - 1]:
                self.file_name.loc[index, 'buyORsell'] = -1

            else:
                self.file_name.loc[index, 'buyORsell'] = 0


    def inside_candle_strategy(self, end_date):
        
        self.cal_signal()

        self.file_name.set_index("date", inplace=True)
        self.file_name.index = pd.to_datetime(self.file_name.index, format="%Y-%m-%d")

        cur_date = self.file_name.index[0]
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

        stop_loss = 0.97
        stop_win = 1.03

        while cur_date != end_date:

            self.stockAccount.execute_limit_order(cur_date=cur_date)

            if len(self.stockAccount.get_portfolios()) == 0 and self.file_name.loc[cur_date, "buyORsell"] == 1:

                price = self.file_name.loc[cur_date + datetime.timedelta(days=1), 'open']
                
                self.stockAccount.send_limit_buy_order(ticker=self.ticker, date=cur_date + datetime.timedelta(days=1), price=price, ls=True)

            if len(self.stockAccount.get_portfolios()) == 1 and (self.file_name.loc[cur_date, "close"] >= self.stockAccount.get_portfolios()[0]['buy_price'] * stop_win or self.file_name.loc[cur_date, "close"] <= self.stockAccount.get_portfolios()[0]['buy_price'] * stop_loss):

                price = self.file_name.loc[cur_date + datetime.timedelta(days=1), 'open']

                self.stockAccount.send_limit_sell_order(ticker=self.ticker, date=cur_date + datetime.timedelta(days=1), price=price, ls=True)

            cur_date += datetime.timedelta(days=1)