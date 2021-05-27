#!/usr/bin/env python
# coding: utf-8

# In[30]:


#Libraries
import pandas as pd
import matplotlib.pyplot as plt
import pandas_datareader as web
import numpy as np
plt.style.use('seaborn-pastel')


# In[31]:


stock = input("Enter Ticker: ")


# In[32]:


OBVMovAv1 = int(input("MA: "))


# In[33]:


OBVMovAv2 = int(input("MA: "))


# In[ ]:


Start = input(" Year-Month-Day: ")


# In[34]:


#Get Stock Data
stock = web.DataReader(stock, data_source='yahoo', start=Start)
stock

#OBV Formula
OBV = []
OBV.append(0)

for i in range(1, len(stock.Close)):
    if stock.Close[i] > stock.Close[i-1]:
        OBV.append (OBV[-1] + stock.Volume[i])
    elif stock.Close[i] < stock.Close[i-1]:
        OBV.append(OBV[-1] - stock.Volume[i])
    else:
        OBV.append (OBV[-1])


# In[35]:


#Get OBV EMA Data
stock['OBV'] = OBV
stock['OBV_EMA'] = stock['OBV'].ewm(span=OBVMovAv1).mean()
stock['OBV_EMA1'] = stock['OBV'].ewm(span=OBVMovAv2).mean()

OBV_EMA = stock['OBV_EMA']
OBV_EMA1 = stock['OBV_EMA1']

stock = stock.dropna()
stock


# In[36]:


#Plot OBV OBV EMA Data
plt.figure(figsize=(16, 8))
plt.plot(stock['OBV'], label = 'OBV', color = 'orange')
plt.plot(stock['OBV_EMA'], label = 'OBV EMA (1)', color = 'purple')
plt.plot(stock['OBV_EMA1'], label = 'OBV EMA (2)', color = 'pink')
plt.title('OBV , OBV EMA (1) , OBV EMA(2)')
plt.xlabel('Date', fontsize = 18)
plt.ylabel('On-Balance Volume', fontsize = 18)
plt.legend(title='OBV Chart', loc='lower right')
plt.show()


# In[37]:


#Incorporate Closing Price into OBV OBV EMA Data
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters ()
x = stock.index
y1 = stock['OBV']
y2 = stock['OBV_EMA']
y3 = stock['OBV_EMA1']
y4 = stock['Close']


fig, ax1 = plt.subplots(figsize=(16, 8))


curve1 = ax1.plot(x, y4, label='Stock Close Price', color='r')

plt.legend(title='Left Y-Axis Legend (Red Side)', loc='upper left')
plt.xlabel('Date', color = 'black', fontsize=18)
plt.ylabel('Adj. Close Price USD ($)', color = 'red', fontsize=18)

ax2 = ax1.twinx()
curve2 = ax2.plot(x, y1, label='OBV (Starts at 0)', color='g')
curve2 = ax2.plot(x, y2, label='OBV EMA (1) (Starts at 0)', color='b')
curve2 = ax2.plot(x, y3, label='OBV EMA (2) (Starts at o)', color='pink')

plt.title('OBV - OBV EMA (1) - OBV EMA(2) - Close', fontsize=18)
plt.ylabel('On-Balance Volume', color = 'blue',fontsize=18)
plt.legend(title='Right Y-Axis Legend (Blue Side)', loc='lower right')
plt.plot()
plt.show()


# In[38]:


#Create a function to signal when to buy and sell an asset
def buy_sell(signal):
  sigPriceBuy = []
  sigPriceSell = []
  flag = -1
  for i in range(0,len(signal)):
    #if MA2 > MA24  then buy else sell
      if signal['OBV_EMA'][i] > signal['OBV_EMA1'][i]:
        if flag != 1:
          sigPriceBuy.append(signal['OBV_EMA'][i])
          sigPriceSell.append(np.nan)
          flag = 1
        else:
          sigPriceBuy.append(np.nan)
          sigPriceSell.append(np.nan)
        #print('Buy')
      elif signal['OBV_EMA'][i] < signal['OBV_EMA1'][i]:
        if flag != 0:
          sigPriceSell.append(signal['OBV_EMA'][i])
          sigPriceBuy.append(np.nan)
          flag = 0
        else:
          sigPriceBuy.append(np.nan)
          sigPriceSell.append(np.nan)
        #print('sell')
      else: #Handling nan values
        sigPriceBuy.append(np.nan)
        sigPriceSell.append(np.nan)
  
  return (sigPriceBuy, sigPriceSell)


# In[39]:


#Create a new dataframe
signal = pd.DataFrame(index=stock['Close'].index)
signal['Close'] = stock['Close']
signal['OBV_EMA'] = OBV_EMA
signal['OBV_EMA1'] = OBV_EMA1


# In[40]:


signal


# In[41]:


x = buy_sell(signal)
signal['Buy_Signal_Price'] = x[0]
signal['Sell_Signal_Price'] = x[1]


# In[42]:


signal


# In[43]:


#Stock Returns Data
stock_daily_returns = stock['Adj Close'].diff()

fig = plt.figure(figsize=(18,10))
ax1 = fig.add_axes([0.1,0.1,0.8,0.8])
ax1.plot(stock_daily_returns)
ax1.set_xlabel("Date")
ax1.set_ylabel("Returns")
ax1.set_title("Stock Daily returns data")
plt.show()


# In[44]:


stock['cum'] = stock_daily_returns.cumsum()
stock.tail()


# In[45]:


fig = plt.figure(figsize=(18,10))
ax1 = fig.add_axes([0.1,0.1,0.8,0.8])
stock['cum'].plot()
ax1.set_xlabel("Date")
ax1.set_ylabel("Growth of $1 investment")
ax1.set_title("Stock daily cumulative returns data")
plt.show()


# In[46]:


# OBV EMA > OBV EMA1 Calculation
stock['Shares'] = [1 if stock.loc[ei, 'OBV_EMA']>stock.loc[ei, 'OBV_EMA1'] else 0 for ei in stock.index]


# In[47]:


#Strategy Profit Plot
stock['Close1'] = stock['Close'].shift(-1)
stock['Profit'] = [stock.loc[ei, 'Close1'] - stock.loc[ei, 'Close'] if stock.loc[ei, 'Shares']==1 else 0 for ei in stock.index]
stock['Profit'].plot(figsize=(18, 10))
plt.axhline(y=0, color='red')
plt.title('Profit')


# In[48]:


#Profit per Day, and Accumulative Wealth
stock['Wealth'] = stock['Profit'].cumsum()
stock.tail()


# In[49]:


stock['diff'] = stock['Wealth'] - stock['cum']
stock.tail()


# In[50]:


stock['pctdiff'] = (stock['diff'] / stock['cum'])*100
stock.tail()


# In[51]:


start = stock.iloc[0]
stock['start'] = start
start['Close']


# In[52]:


start1 = start['Close']
stock['start1'] = start1
stock


# In[54]:


#Plot the Data with Buy and Sell Signals
my_stocks = signal
ticker = 'Close'

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters ()

fig, ax1 = plt.subplots(figsize=(18, 10))

plt.rc('axes',edgecolor='navy')

plt.annotate('$\it{Data Source: Yahoo Finance}$', xy=(0.02, 0.05), xycoords='axes fraction', color='navy')
plt.annotate('Program by: Taylor Bommarito', xy=(0.02, 0.08), xycoords='axes fraction', color='navy')
plt.annotate('1 Share of Stock from Buy and Hold Strategy is : ${:.2f}'.format(stock.loc[stock.index[-2],'cum']), xy=(0.23, 1.13), xycoords='axes fraction', fontsize=18, weight='bold', color='navy')
plt.annotate('Strategy difference is : ${:.2f}'.format(stock.loc[stock.index[-2],'diff']), xy=(0.34, 1.075), xycoords='axes fraction', fontsize=18, weight='bold', color='navy')
plt.annotate('Strategy Percent Improvement : {:.3f}%'.format(stock.loc[stock.index[-2],'pctdiff']), xy=(0.28, 1.02), xycoords='axes fraction', fontsize=18, weight='bold', color='navy')

ax1.set_facecolor('white')

ax1.grid(False)

ax1.tick_params(axis='y', colors='red')


curve1 = ax1.plot(my_stocks[ticker],  label='Stock Close Price Starts at : ${:.2f}'.format(stock.loc[stock.index[-2],'start1']), color='olive', linewidth= 1.5, alpha = 0.50)
#curve1 = ax1.plot(stock['Wealth'], label='Wealth Accumulation (Starts at $0)', color='red')
plt.legend(title='Left Y-Axis Legend (Red Side)', loc='upper left')
plt.xlabel('Date', color = 'navy', fontsize=18, weight='bold')
plt.ylabel('Close Price USD ($)', color = 'red',fontsize=18, weight='bold')

ax2 = ax1.twinx()
ax2.grid(False)
curve2 = ax2.plot(stock['OBV'], label=' Real OBV (Starts at 0)', color='yellow', linewidth= 1.5)
curve2 = ax2.plot(my_stocks['OBV_EMA'], label='OBV EMA (1) (Starts at 0)', color='orange', linewidth= 1.5)
curve2 = ax2.plot(my_stocks['OBV_EMA1'], label='OBV EMA (2) (Starts at 0)',color='blue', linewidth= 1.5, alpha = 0.35)
curve2 = ax2.plot(my_stocks.index, my_stocks['Buy_Signal_Price'], color = 'green', label='Buy Signal', marker = '^', alpha = 1)
curve2 = ax2.plot(my_stocks.index, my_stocks['Sell_Signal_Price'], color = 'red', label='Sell Signal', marker = 'v', alpha = 1)
plt.title('1 Share of Stock from OBV EMA(1) > OBV EMA (2) Strategy is : ${:.2f}'.format(stock.loc[stock.index[-2],'Wealth']), color = 'navy', fontsize=18, weight='bold', pad=100)
plt.ylabel('On-Balance Volume', color = 'blue',fontsize=18, weight='bold')
plt.legend(title='Right Y-Axis Legend (Blue Side)', loc='lower right')


ax1.tick_params(axis='x', colors='navy')
ax2.tick_params(axis='y', colors='blue')


plt.plot()
plt.show()


# In[55]:


#Accumulative Wealth from Strategy Chart
fig, ax1 = plt.subplots(figsize=(18, 10))

plt.rc('axes',edgecolor='navy')

plt.annotate('$\it{Data Source: Yahoo Finance}$', xy=(0.02, 0.05), xycoords='axes fraction', color='navy')
plt.annotate('Program by: Taylor Bommarito', xy=(0.02, 0.08), xycoords='axes fraction', color='navy')
plt.annotate('1 Share of Stock from Buy and Hold Strategy is : ${:.2f}'.format(stock.loc[stock.index[-2],'cum']), xy=(0.23, 1.13), xycoords='axes fraction', fontsize=18, weight='bold', color='navy')
plt.annotate('Strategy difference is : ${:.2f}'.format(stock.loc[stock.index[-2],'diff']), xy=(0.34, 1.075), xycoords='axes fraction', fontsize=18, weight='bold', color='navy')
plt.annotate('Strategy Percent Improvement : {:.3f}%'.format(stock.loc[stock.index[-2],'pctdiff']), xy=(0.28, 1.02), xycoords='axes fraction', fontsize=18, weight='bold', color='navy')

ax1.set_facecolor('white')

ax1.grid(False)

ax1.tick_params(axis='x', colors='navy')
ax1.tick_params(axis='y', colors='red')

plt.plot(stock['Wealth'], label='OBV Wealth Accumulation $$$$ (Starts at $0)', color='green')
plt.plot(stock['cum'], label='Buy Hold Wealth Accumulation $$$$ (Starts at $0)', color='blue', alpha=0.35)
plt.legend( loc='upper left')
plt.xlabel('Date', color = 'navy', fontsize=18, weight='bold')
plt.ylabel('Amount Earned USD ($)', color = 'red', fontsize=18, weight='bold')
plt.title('1 Share of Stock from OBV EMA(1) > OBV EMA (2) Strategy is : ${:.2f}'.format(stock.loc[stock.index[-2],'Wealth']), color = 'navy', fontsize=18, weight='bold', pad=100)


# In[ ]:





# In[ ]:




