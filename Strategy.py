class StockAccount():

    def __init__(self) -> None:
        self.pls = []
        self._buy_orders = []
        self._sell_orders = []
        self.transactions = []
        self.portfolio = []


    def send_buy_order(self, ticker, date, price) -> None:
        # 5
        buy_order = {'ticker': ticker, 'date': date, 'price': price, 'buy': True}
        self._buy_orders.append(buy_order)


    def send_sell_order(self, ticker, date, price) -> None:
        sell_order = {'ticker': ticker, 'date': date, 'price': price, 'buy': False}
        self._sell_orders.append(sell_order)


    def execute_order(self, cur_date) -> None:
        for i in self._buy_orders:
            if i['date'] == cur_date:
                self.transactions.append(i)
                self.portfolio.append(i)
                self._buy_orders.pop()
                break

        for i in self._sell_orders:
            if i['date'] == cur_date:
                self.transactions.append(i)

                buy_price = self.portfolio[0]['price']
                sell_price = i['price']
                pl = sell_price - buy_price
                pl_percent = ((sell_price - buy_price) / buy_price) * 100
                pl = {'ticker': i['ticker'], 'buy_date': self.portfolio[0]['date'], 'buy_price': buy_price, 'sell_date': i['date'], 'sell_price': sell_price, 'pl': pl, 'pl_percent': pl_percent}
                self.pls.append(pl)

                self.portfolio.pop()
                self._sell_orders.pop()
                break


    def get_strategy_info(self) -> dict:
        win = 0 # no of win trades
        loss = 0 # no of loss trades

        max_win = 0
        max_loss = 0
        
        sum_pl_percent = 0
        accumulated_percent = 1

        for i in self.pls:
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

        info_statment = {'average_return_per_trade': sum_pl_percent / len(self.pls),
                         'accumulated_return': (accumulated_percent - 1) * 100,
                         'win_ratio': (win / loss) * 100,
                         'max_win': max_win,
                         'max_loss': max_loss,
                         'total_trade': len(self.pls)}
        
        return info_statment