import pandas as pd

class Investment():

    def __init__(self) -> None:
        self.dailydata = pd.DataFrame()
        self.support_value = 0
        self.resistance_value = 0
        self.stop_loss = 0

    def read_data(self) -> None:
        self.dailydata = pd.read_csv("BTC-USDT_daily.csv",parse_dates=['date'])


    def cal_signal(self) -> None:

        # Find the maximum value from the first day's high
        max_value = self.dailydata['high'].iloc[0]

        # Find the minimum value from the second day's low
        min_value = self.dailydata['low'].iloc[0]

        self.dailydata['max_value'] = None
        self.dailydata['min_value'] = None
        self.dailydata.loc[0, 'max_value'] = self.dailydata['high'].iloc[0]
        self.dailydata.loc[0, 'min_value'] = self.dailydata['low'].iloc[0]

        self.dailydata['signal'] = None
        self.dailydata.loc[0, 'signal'] = 0
        # Loop through the DataFrame from the second day onwards
        for i in range(1, len(self.dailydata)):
            # Check if the high value is greater than the current interval max
            if self.dailydata['close'].iloc[i] > self.dailydata.loc[i - 1, 'max_value']:
                # Update the maximum value of the interval range
                self.dailydata.loc[i, 'max_value'] = self.dailydata['high'].iloc[i]
                self.dailydata.loc[i, 'min_value'] = self.dailydata['low'].iloc[i]
                self.dailydata.loc[i, 'signal'] = 0
            # Check if the low value is less than the current interval min
            elif self.dailydata['close'].iloc[i] < self.dailydata.loc[i - 1, 'min_value']:
                # Update the minimum value of the interval range
                self.dailydata.loc[i, 'max_value'] = self.dailydata['high'].iloc[i]
                self.dailydata.loc[i, 'min_value'] = self.dailydata['low'].iloc[i]
                self.dailydata.loc[i, 'signal'] = 0

            else:
                self.dailydata.loc[i, 'max_value'] = self.dailydata['max_value'].iloc[i - 1]
                self.dailydata.loc[i, 'min_value'] = self.dailydata['min_value'].iloc[i - 1]
                self.dailydata.loc[i, 'signal'] = self.dailydata.loc[i - 1, 'signal'] + 1

        self.dailydata['signal_diff'] = self.dailydata['signal'].diff()
        self.dailydata['buyORsell'] = 0
        for index, row in self.dailydata.iterrows():
            if row['signal_diff'] <= -3 and row['close'] > self.dailydata['max_value'].iloc[index - 1]:
                self.dailydata.loc[index, 'buyORsell'] = 1
            elif row['signal_diff'] <= -3 and row['close'] < self.dailydata['min_value'].iloc[index - 1]:
                self.dailydata.loc[index, 'buyORsell'] = -1
            else:
                self.dailydata.loc[index, 'buyORsell'] = 0