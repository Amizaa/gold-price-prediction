import backtrader as bt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime


df = pd.read_excel ("LSTM_prediction_result.xlsx")
df['date'] = pd.to_datetime(df['date'], format='%Y.%m.%d')
df.set_index('date', inplace=True)
df = df.replace([np.inf, -np.inf], np.nan)
df.dropna(subset=['close', 'predicted'], inplace=True)
df['volume'] = 1000


df["close"] = df["close"].astype(float)
df["predicted"] = df["predicted"].astype(float)



# Create a Data Feed
class LSTMPredictionData(bt.feeds.PandasData):
    lines = ('predicted',)
    params = (
        ('datetime', None),
        ('open', 'open'),
        ('high', 'high'),
        ('low', 'low'),
        ('close', 'close'),
        ('volume', 'volume'),
        ('openinterest', -1),
        ('predicted', 'predicted'),
    )
       
    

# LSTM-based Strategy
class LSTMStrategy(bt.Strategy):
    params = (
        ('threshold', 0.001), 
    )
    
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')
        
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.datapredicted = self.datas[0].predicted
        
        # Keep track of pending orders
        self.order = None
        self.buyprice = None
        self.buycomm = None
        
        # Add indicators
        self.pred_pct_diff = bt.indicators.PercentChange(
            (self.datapredicted(0) / self.dataclose(-1)), period=1)
        
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Order submitted/accepted - nothing to do
            return

        # Check if an order has been completed
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
                
            self.bar_executed = len(self)
            
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
            
        self.order = None
    
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
            
        self.log(f'OPERATION PROFIT, GROSS: {trade.pnl:.2f}, NET: {trade.pnlcomm:.2f}')
        
    def next(self):
        # Log the closing price
        self.log(f'Close: {self.dataclose[0]:.2f}, Predicted: {self.datapredicted[0]:.2f} Value:{cerebro.broker.getvalue()}')
        
        # Check if an order is pending
        if self.order:
            return
            
        # Check if we are in the market
        if not self.position:
            # We are not in the market, look for buy signal
            if self.datapredicted[0] > self.dataclose[0] * (1 + self.params.threshold):
                # Predicted price is higher than current by threshold -> BUY
                self.log(f'BUY CREATE, {self.dataclose[0]:.2f} Value:{cerebro.broker.getvalue()}')
                self.order = self.buy()
                
        else:
            # We are in the market, look for sell signal
            if self.datapredicted[0] < self.dataclose[0] * (1 - self.params.threshold):
                # Predicted price is lower than current by threshold -> SELL
                self.log(f'SELL CREATE, {self.dataclose[0]:.2f}')
                self.order = self.sell()

# Create a Cerebro entity
cerebro = bt.Cerebro()

# Add a strategy
cerebro.addstrategy(LSTMStrategy)

# Create a Data Feed
data = LSTMPredictionData(dataname=df)

# Add the Data Feed to Cerebro
cerebro.adddata(data)

# Set our desired cash start
cerebro.broker.setcash(100000.0)

# Add a FixedSize sizer
cerebro.addsizer(bt.sizers.FixedSize, stake=10)

# Set the commission
cerebro.broker.setcommission(commission=0.001) 

# Print out the starting conditions
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

# Run over everything
cerebro.run()

# Print out the final result
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

# Plot the result
cerebro.plot(style='candlestick')