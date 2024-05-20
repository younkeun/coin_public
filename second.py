import pyupbit
import time
import pandas as pd


MONEY = 800000  # 매수할 금액


# 최근 1분 거래대금 높은 종목 찾기
def get_top_volume_coins(n=20):
    tickers = pyupbit.get_tickers(fiat="KRW")  # 코인 전체 목록 조회
    volume_dict = {}  # 종목별 거래대금 저장하는 곳

    # 최근 1분 거래대금 조회
    for ticker in tickers:
        df = pyupbit.get_ohlcv(ticker, interval="minute1", count=1)
        if df is not None:
            volume = df['volume'].iloc[0] * df['close'].iloc[0]  # 거래대금 = 거래량 * 종가
            volume_dict[ticker] = volume

    # 거래대금 상위 N개
    top_volume_coins = sorted(volume_dict, key=volume_dict.get, reverse=True)[:n]
    return top_volume_coins

# 1분 전 가격 대비 현재 가격 - 변동률
def get_percent_change(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="minute1", count=2) # 비교대상 : 1분전
    if df is not None and len(df) == 2:
        prev_close = df['close'].iloc[0]
        current_close = df['close'].iloc[1]
        percent_change = (current_close - prev_close) / prev_close * 100
        return percent_change
    return None

# 1분 전 가격 대비 현재 가격이 1% 이상 상승 종목
def select_coins():
    top_coins = get_top_volume_coins()
    selected_coins = []
    for coin in top_coins:
        percent_change = get_percent_change(coin)
        if percent_change is not None and percent_change >= 0.5:
            selected_coins.append(coin)
    return selected_coins

# [거래대금 + 상승률] 조건 맞는애들 + 잔고확인해서 매수해라 
# 잔고 확인: 1) 70만원만 사고, 2) 70만원 넘게 보유했으면 사지말고, 3) 현금 70보다 적으면 가지고 있는만큼만  
def buy_coins():
    selected_coins = select_coins()
    for coin in selected_coins:
        coin_balance = upbit.get_balance(coin)
        if coin_balance < MONEY: # 잔고 확인2
            current_price = pyupbit.get_current_price(coin)
            orderbook = pyupbit.get_orderbook(coin)
            ask_price = orderbook['orderbook_units'][0]['ask_price'] + tick_size(coin)
            if ask_price > current_price:
                upbit.buy_market_order(coin, min(MONEY, upbit.get_balance("KRW")-1000))  # 잔고 확인 1, 3 

# 호가
def tick_size(ticker):
    price = pyupbit.get_current_price(ticker)
    if price >= 2000000:
        return round(price / 1000) * 1000
    elif price >= 1000000:
        return round(price / 500) * 500
    elif price >= 100000:
        return round(price / 100) * 100
    elif price >= 10000:
        return round(price / 50) * 50
    elif price >= 1000:
        return round(price / 10) * 10
    else:
        return round(price)


# 매도 조건 설정: 보유종목 중에, 1분 전 가격 대비 1% 이상 하락 or 거래대금 20위 밖으로 밀리면 전량 매도
def sell_coins():
    owned_coins = upbit.get_balances()
    coins_to_sell = []
    for coin in owned_coins:
        if coin['currency'] == "KRW":
            continue
        ticker = "KRW-" + coin['currency']
        percent_change = get_percent_change(ticker)
        if (percent_change is not None and percent_change <= -0.5):
            coins_to_sell.append(ticker)
    for coin in coins_to_sell:
        coin_balance = upbit.get_balance(coin)
        if coin_balance > 0:
            upbit.sell_market_order(coin, coin_balance)


# # 로그인 집
# access = "vpcyaebgyzpHesluQbrzxiFpvrViJkVLnZPKlDGJ"
# secret = "U25fsLQudrykGHxWS2CLpm4i2yU0xptRRMfL7yaF"
# upbit = pyupbit.Upbit(access, secret)


# # 로그인 회사
# access_key = "usQAxh2mbfbaGPSGxu8YvaMoWtoTzy9N9gPW0VmI"
# secret_key = "BNUhu4ofcbyZZngfCl5wsm79lKwPmSJbzktGWE1h"
# upbit = pyupbit.Upbit(access_key, secret_key)


# 로그인 AWS
access_key = "M9Oqzn31t6Xo22hoZd8FxxtiarsEFxQpLzy0luAx"
secret_key = "DBM29xlxEi60IgmX6D1zpqqRWhwuH1xSuUgbh4RY"
upbit = pyupbit.Upbit(access_key, secret_key)


# 실행
while True:
    buy_coins()
    sell_coins()



# 참고 
    top_coins = get_top_volume_coins(10)
    for coin in top_coins:
        percent_change = get_percent_change(coin)
        print(f"{coin}: {percent_change}%")

    time.sleep(10)
