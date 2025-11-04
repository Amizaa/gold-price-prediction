import backtrader as bt
import pandas as pd


# Define LSTM-based strategy

class LSTMStrategy(bt.Strategy):
    def next(self):
       
        
        if self.position:
            if self.datas[0].predicted[0] < self.datas[0].close[0]:
                self.close()
        else:
            if self.datas[0].predicted[0] > self.datas[0].close[0]:
                self.buy()


# Custom data feed with predicted prices
class PredictedCSV(bt.feeds.PandasData):
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

    

# Load your CSV (should contain Date, Close, Predicted)
df = pd.read_excel ("LSTM_prediction_result.xlsx")
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)
import numpy as np
df = df.replace([np.inf, -np.inf], np.nan)
df = df.dropna(subset=['close', 'predicted'])
df['volume'] = 100

# Backtrader setup
cerebro = bt.Cerebro()
data = PredictedCSV(dataname=df)

cerebro.adddata(data)
cerebro.addstrategy(LSTMStrategy)
cerebro.broker.setcash(100000.0)

cerebro.addsizer(bt.sizers.FixedSize, stake=10)

# Set the commission
cerebro.broker.setcommission(commission=0.001)  

print(f"Starting Portfolio Value: {cerebro.broker.getvalue():.2f}")
cerebro.run()
print(f"Final Portfolio Value: {cerebro.broker.getvalue():.2f}")

cerebro.plot(style='candlestick')
