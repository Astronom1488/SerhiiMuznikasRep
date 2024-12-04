import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import numpy as np
import pandas as pd
import statsmodels.api as sm
from binance import Client
from futures_sign import send_signed_request
from cred import KEY, SECRET
pd.set_option('display.max_columns', None)
client = Client(KEY, SECRET)
TARGET_CHAT_ID = -1001525141301
MESSAGE_THREAD_ID = 1452

def indSlope(series, n):
    array_sl = [j * 0 for j in range(n - 1)]

    for j in range(n, len(series) + 1):
        y = series[j - n:j]
        x = np.array(range(n))
        x_sc = (x - x.min()) / (x.max() - x.min())
        y_sc = (y - y.min()) / (y.max() - y.min())
        x_sc = sm.add_constant(x_sc)
        model = sm.OLS(y_sc, x_sc)
        results = model.fit()
        array_sl.append(results.params.iloc[-1])
    slope_angle = (np.rad2deg(np.arctan(np.array(array_sl))))
    return np.array(slope_angle)


# True Range and Average True Range indicator
def indATR(source_DF, n):
    df = source_DF.copy()
    df['H-L'] = abs(df['high'] - df['low'])
    df['H-PC'] = abs(df['high'] - df['close'].shift(1))
    df['L-PC'] = abs(df['low'] - df['close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1, skipna=False)
    df['ATR'] = df['TR'].rolling(n).mean()
    df_temp = df.drop(['H-L', 'H-PC', 'L-PC'], axis=1)
    return df_temp

# generate data frame with all needed data
def PrepareDF(DF):
    ohlc = DF.iloc[:, [0, 1, 2, 3, 4, 5]]
    ohlc.columns = ["date", "open", "high", "low", "close", "volume"]
    ohlc = ohlc.set_index('date')
    df = indATR(ohlc, 14).reset_index()
    df['slope'] = indSlope(df['close'], 5)
    df['channel_max'] = df['high'].rolling(10).max()
    df['channel_min'] = df['low'].rolling(10).min()
    df['position_in_channel'] = (df['close'] - df['channel_min']) / (df['channel_max'] - df['channel_min'])
    df = df.set_index('date')
    df = df.reset_index()
    return df

def get_futures_klines(symbol,limit):
    x = requests.get('https://binance.com/fapi/v1/klines?symbol='+symbol+'&limit='+str(limit)+'&interval=15m')
    df=pd.DataFrame(x.json())
    df.columns=['open_time','open','high','low','close','volume','close_time','d1','d2','d3','d4','d5']
    df=df.drop(['d1','d2','d3','d4','d5'],axis=1)
    df['open']=df['open'].astype(float)
    df['high']=df['high'].astype(float)
    df['low']=df['low'].astype(float)
    df['close']=df['close'].astype(float)
    df['volume']=df['volume'].astype(float)
    return(df)

def open_position(symbol, s_l, balance_percent, leverage):

    avg_price_res = client.get_avg_price(symbol=symbol)
    avg_price = float(avg_price_res['price'])

    money_in_account = get_balance_on_account()
    quantity = ((money_in_account * balance_percent / 100) / avg_price) * leverage

    quantity = round(quantity, 0)
    client.futures_change_leverage(symbol=symbol, leverage=leverage)
    params = {
        "batchOrders": [
            {
                "symbol": symbol,
                "side": "BUY" if s_l == 'long' else "SELL",
                "type": "MARKET",
                "quantity": str(quantity),
            }
        ]
    }
    response = send_signed_request('POST', '/fapi/v1/batchOrders', params)

def close_position(symbol, s_l, quantity, leverage):

    client.futures_change_leverage(symbol=symbol, leverage=leverage)
    params = {
        "batchOrders": [
            {
                "symbol": symbol,
                "side": "BUY" if s_l == 'short' else "SELL",
                "type": "MARKET",
                "quantity": str(quantity),
            }
        ]
    }

    response = send_signed_request('POST', '/fapi/v1/batchOrders', params)

def check_and_close_orders(symbol):
    global isStop
    a=client.futures_get_open_orders(symbol=symbol)
    if len(a)>0:
        isStop = False
        client.futures_cancel_all_open_orders(symbol=symbol)

def get_symbol_price(symbol):
    prices = client.get_all_tickers()
    df=pd.DataFrame(prices)
    return float(df[df['symbol'] == symbol]['price'].iloc[0])

def get_opened_positions(symbol):
    status = client.futures_account()
    positions = pd.DataFrame(status['positions'])
    position_amount = positions[positions['symbol'] == symbol]['positionAmt'].astype(float).tolist()[0]
    leverage = int(positions[positions['symbol'] == symbol]['leverage'].iloc[0])
    entry_price = float(positions[positions['symbol'] == symbol]['entryPrice'].iloc[0])
    profit = float(status['totalUnrealizedProfit'])
    balance = round(float(status['totalWalletBalance']), 2)
    if position_amount > 0:
        position_type = "long"
    elif position_amount < 0:
        position_type = "short"
    else:
        position_type = ""
    price_now = get_symbol_price(symbol)
    if entry_price > 0:
        PnL = (((price_now - entry_price) / entry_price) * leverage) * 100
    else:
        PnL = 0
    return [position_type, position_amount, profit, leverage, balance, round(entry_price, 3), PnL]

def get_balance_on_account():
    money = 0
    futures_info = client.futures_account()
    for asset_info in futures_info['assets']:
        if asset_info['asset'] == 'USDT':
            money = float(asset_info['walletBalance'])
    return money


def get_trading_signal(symbol, time):
    driver = webdriver.Chrome()
    url = f'https://ru.tradingview.com/symbols/{symbol}/technicals/?exchange=CRYPTO'
    driver.get(url)
    try:
        button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, time)))
        button.click()
        time.sleep(1)
        # Общая оценка
        element = WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div[4]/div[2]/div[2]/div/section/div/div[2]/div[3]/div[2]/div[1]/div[3]')))
        signal = element.text
    except:
        signal = "neutral"

    driver.quit()
    return signal

    # if meaning == "Активно покупать":
    #     signal = "longMAX"
    # elif meaning == "Покупать":
    #     signal = "long"
    # elif meaning == "Активно продавать":
    #     signal = "shortMAX"
    # elif meaning == "Продавать":
    #     signal = "short"
    # else:
    #     signal = "neutral"

def SendMessageOnTelegram(bot, pointer, message, text):
    bot.reply_to(message, pointer + ": " + text)
    bot.send_message(TARGET_CHAT_ID,  pointer + ": " + text, message_thread_id=MESSAGE_THREAD_ID)



