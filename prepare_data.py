import pandas as pd

def to_dataframe(name):
    df = pd.read_csv(f'./prev_etf_data/{name}.csv')[['Date', 'Price']].loc[::-1].reset_index()
    df['Date'] = pd.to_datetime(df['Date'], infer_datetime_format=True).dt.date
    df[name] = df['Price']
    return df[['Date', name]]

def merge(left, right):
    return pd.merge(left, right, left_on='Date', right_on='Date', how='outer').sort_values('Date')

bil_dt = to_dataframe('BIL')
bnd_dt = to_dataframe('BND')
ief_dt = to_dataframe('IEF')
lqd_dt = to_dataframe('LQD')
pdbc_dt = to_dataframe('PDBC')
qqq_dt = to_dataframe('QQQ')
spy_dt = to_dataframe('SPY')
tip_dt = to_dataframe('TIP')
tlt_dt = to_dataframe('TLT')
vea_dt = to_dataframe('VEA')
vwo_dt = to_dataframe('VWO')


#-----공격자산------
data = merge(qqq_dt, vwo_dt)
data = merge(data, vea_dt)
data = merge(data, bnd_dt)

data = data.set_index(['Date'])
data = data.dropna() # <class 'pandas.core.frame.DataFrame'>
print(data.index[0]) # 2007-07-27
data.to_csv('./next_etf_data/aggressive.csv')


# #-----안전자산-----
# data = merge(tip_dt, pdbc_dt)
# data = merge(data, bil_dt)
# data = merge(data, ief_dt)
# data = merge(data, tlt_dt)
# data = merge(data, lqd_dt)
# data = merge(data, bnd_dt)

# data.sort_index()
# data = data.dropna()
# data.to_csv('./next_etf_data/defensive.csv')


# #-----카나리아자산-----
# data = merge(spy_dt, vea_dt)
# data = merge(data, vwo_dt)
# data = merge(data, bnd_dt)

# data.sort_index()
# data = data.dropna()
# data.to_csv('./next_etf_data/canary.csv')






