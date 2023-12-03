import pandas as pd
import numpy as np
import yfinance as yf
import quantstats as qs 
from collections import defaultdict
import matplotlib.pyplot as plt 

# yahoo finance에서 필요한 정보를 가져온다!
def get_data(tickers, type="Adj Close"):
    df = yf.download(tickers)
    df = df[type]
    df.dropna(inplace=True) # null값 제거
    return df


def get_rebalance_data(df, rebal="month"):
    res_df = pd.DataFrame()
    df['year'] = df.index.year
    df['month'] = df.index.month
    df['day'] = df.index.day

    # 월 말 데이터 구하기
    date_df = df.groupby(['year', 'month'])['day'].max()
    #     year  month
    # 2014  11       28
    #       12       31
    # 2015  1        30
    #       2        27
    #       3        31

    # 데이터 합치기
    for i in range(len(date_df)):
        day = '{}-{}-{}'.format(date_df.index[i][0], date_df.index[i][1], date_df.iloc[i])
        res_df = pd.concat([res_df, df[df.index==day]])

    return res_df
    #                   BIL        BND        DBC  ...  year  month  day
    # Date                                         ...
    # 2014-11-28  82.709671  65.209091  19.721268  ...  2014     11   28       
    # 2014-12-31  82.691605  65.246094  17.818680  ...  2014     12   31  


tickers_canary = ['SPY', 'VWO', 'VEA', 'BND']   # 카나리아자산
tickers_g4 = ['QQQ', 'VWO', 'VEA', 'BND']       # 공격자산
tickers_g12 = ['SPY', 'QQQ', 'IWM', 'VGK', 'EWJ', 'EEM', 'VNQ', 'DBC', 'GLD', 'TLT', 'HYG', 'LQD'] # balance형
tickers_safe = ['TIP', 'BIL', 'PDBC', 'IEF', 'TLT', 'LQD', 'BND']   # 안전자산

tickers_all = list(set(tickers_canary+tickers_g4+tickers_g12+tickers_safe))

# 종목 전체
data = get_data(tickers_all)
# 월말 데이터
rebalance_data = get_rebalance_data(data)

baa_g4 = pd.DataFrame(columns=tickers_all)
# [PDBC, VWO, BIL, IWM, LQD, TLT, EEM, SPY, EWJ, VEA, VGK, GLD, DBC, QQQ, IEF, VNQ, TIP, HYG, BND]
res = []

canary_data = rebalance_data[tickers_canary]
profit = rebalance_data.pct_change() # (다음행-현재행) / 현재행
n = 12


# 모멘텀 스코어는 12개월 데이터가 쌓인 이후 계산 가능
# 12부터 data행 개수만큼 for문
for i in range(n, rebalance_data.shape[0]):
    m1 = (canary_data.iloc[i]-canary_data.iloc[i-1])/canary_data.iloc[i-1]
    m3 = (canary_data.iloc[i]-canary_data.iloc[i-3])/[i-3]
    m6 = (canary_data.iloc[i]-canary_data.iloc[i-6])/canary_data.iloc[i-6]
    m12 = (canary_data.iloc[i]-canary_data.iloc[i-12])/canary_data.iloc[i-12]
    score = m1*12 + m3*4 + m6*2 +m12 # 모멘텀 스코어
    buy = defaultdict(int)

    # 카나리아 시그널 발생(모멘텀 스코어 0이하인 자산이 생겼을 때)
    if min(score) <= 0: 
        # 최근 수익 계산: 현재 가격/ 12개월 이동 평균  
        safe = rebalance_data[tickers_safe].iloc[i] / rebalance_data[tickers_safe].iloc[i-n:i].mean()
        safe_top3 = safe.nlargest(3, keep='all') # 수익률이 가장 높은 안전자산 3가지 
        for j in range(3):
            if safe_top3.iloc[j] > safe["BIL"]: # BIL보다 수익률이 크다면 그대로 투자
                name = safe_top3.index[j]
            else:
                name = "BIL"
            buy[name] += (1/3)*100
    else:
        aggresive = rebalance_data[tickers_g4].iloc[i] / rebalance_data[tickers_g4].iloc[i-n:i].mean()
        agg_top1 = aggresive.nlargest(1)
        buy[agg_top1.index[0]] = 100 # 모멘텀 스코어가 가장 높은 스코어에 포트폴리오 100% 투자
    

    if i == n:
        temp = pd.DataFrame([list(buy.values())], columns=list(buy.keys()), index = [rebalance_data.index[i]])
        baa_g4 = pd.concat([baa_g4, temp])
        res.append(100)

    else:
        total = sum(((1+profit.iloc[i])*baa_g4.iloc[-1]).fillna(0))
        res.append(total)
        # 비율을 어떻게 해서 투자했는지
        temp = pd.DataFrame([list(buy.values())], columns=list(buy.keys()), index = [rebalance_data.index[i]]) * total / 100
        baa_g4 = pd.concat([baa_g4, temp])


# 누적 수익률
baa_g4["Total"] = res
baa_g4['Daily_rtn'] = baa_g4['Total'].pct_change() # 단순 수익률
baa_g4['St_rtn'] = (baa_g4['Daily_rtn']+1).cumprod() # 누적 수익률
baa_g4['St_rtn'].plot()
# plt.savefig('St_rtn')


# CAGR
total_year = len(set(baa_g4.index.year))
CAGR = baa_g4['St_rtn'].iloc[-1] ** (1/total_year) - 1
print('CAGR: ', CAGR)

# MDD
historical_max = baa_g4['Total'].cummax() # 관측 기간 최고점 가격
daily_drawdown = baa_g4['Total']/historical_max - 1 # 최고점에 비해 얼마나 떨어졌는가?
MDD = daily_drawdown.cummin()
print('MDD: ', MDD)


# SHARPE
# 무위험수익률/연간 표준편차
# np.std: 표준편차, np.sqrt: 제곱근
VOL = np.std(baa_g4['Daily_rtn']) * np.sqrt(len(baa_g4['Daily_rtn']))
SHARPE = np.mean(baa_g4['Daily_rtn'])/ VOL
print('SHARPE: ', SHARPE)