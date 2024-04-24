import sys

class StockAccount():

    def __init__(self) -> None:
        """
        pl structure
            - ticker
            - buy_date
            - buy_price
            - sell_date
            - sell_price
            - pl
            - pl_percent
        """
        self._pls = []
        """
        order structure
            - ticker
            - date
            - price
            - ls: long is True / short is False
            - buy: False
        """
        self._buy_orders = []
        self._sell_orders = []
        """
        transaction structure
            - ticker
            - date
            - price
            - ls: long is True / short is False
            - buy: False
        """
        self._transactions = []
        """
        portfolio structure
            - ticker
            - buy_date
            - buy_price
            - sell_date
            - sell_price
            - ls
        """
        self._portfolios = []

    def get_transaction(self):
        return self._transactions
    

    def get_pls(self):
        return self._pls
    
    def get_portfolios(self):
        return self._portfolios


    def send_limit_buy_order(self, ticker, date, price, ls) -> None:
        
        buy_order = {'ticker': ticker, 'date': date, 'price': price, 'ls': ls, 'buy': True}
        self._buy_orders.append(buy_order)


    def send_limit_sell_order(self, ticker, date, price, ls) -> None:
        
        sell_order = {'ticker': ticker, 'date': date, 'price': price, 'ls': ls, 'buy': False}
        self._sell_orders.append(sell_order)


    def execute_limit_order(self, cur_date) -> None:

        for i in self._buy_orders:
            if i['date'] == cur_date:
    
                if i['ls'] == True: # start a long portfolio
                    new_portfolio = {
                        'ticker': i['ticker'], 
                        'buy_date': i['date'], 
                        'buy_price': i['price'], 
                        'sell_date': None,
                        'sell_price': None,
                        'ls': i['ls'], 
                    }
                    self._portfolios.append(new_portfolio)

                else: # close a short portfolio

                    for portfolio in self._portfolios:

                        if portfolio['ls'] == False:
                            
                            buy_price = i['price']

                            sell_price = portfolio['sell_price']

                            pl = sell_price - buy_price
                            
                            pl_percent = (pl / sell_price) * 100
                            
                            pl = {
                                'ticker': portfolio['ticker'], 
                                'buy_date': i['date'], 
                                'buy_price': i['price'], 
                                'sell_date': portfolio['sell_date'], 
                                'sell_price': portfolio['sell_price'],
                                'ls': False,
                                'pl': pl,
                                'pl_percent': pl_percent
                            }

                            self._portfolios.remove(portfolio)

                            self._pls.append(pl)

                            break


                self._transactions.append(i)

                self._buy_orders.pop()
             

        for i in self._sell_orders:
            if i['date'] == cur_date:

                if i['ls'] == True: # close a long portfolio

                    for portfolio in self._portfolios:

                        if portfolio['ls'] == True:
                            
                            buy_price = portfolio['buy_price']

                            sell_price = i['price']

                            pl = sell_price - buy_price
                            
                            pl_percent = ((sell_price - buy_price) / buy_price) * 100
                            
                            pl = {
                                'ticker': portfolio['ticker'], 
                                'buy_date': portfolio['buy_date'], 
                                'buy_price': portfolio['buy_price'], 
                                'sell_date': i['date'], 
                                'sell_price': i['price'],
                                'ls': True, 
                                'pl': pl,
                                'pl_percent': pl_percent
                            }

                            self._portfolios.remove(portfolio)

                            self._pls.append(pl)

                            break
                    
                else: # start a short portfolio

                    # set up a new portfolio
                    new_portfolio = {
                        'ticker': i['ticker'], 
                        'buy_date': None, 
                        'buy_price': None, 
                        'sell_date': i['date'],
                        'sell_price': i['price'],
                        'ls': i['ls'], 
                    }

                    self._portfolios.append(new_portfolio)

                self._transactions.append(i)

                self._sell_orders.pop()


    def get_strategy_info(self) -> dict:
        win = 0 # no of win trades
        loss = 0 # no of loss trades

        max_win = 0
        max_loss = 0
        
        sum_pl_percent = 0
        accumulated_percent = 1

        for i in self._pls:
            sum_pl_percent += i['pl_percent']
            accumulated_percent *= (i['pl_percent'] / 100) + 1

            if i['pl_percent'] > 0:
                win += 1
                if i['pl_percent'] > max_win:
                    max_win = i['pl_percent']
            else:
                loss += 1
                if i['pl_percent'] < max_loss:
                    max_loss = i['pl_percent']

        info_statment = {'average_return_per_trade': sum_pl_percent / len(self._pls),
                         'accumulated_return': (accumulated_percent - 1) * 100,
                         'win_ratio': (win / (win+loss)) * 100,
                         'max_win': max_win,
                         'max_loss': max_loss,
                         'total_trade': len(self._pls)}
        
        return info_statment