# BAA 알고리즘 백테스트
# 수익률 계산은 "일별"로 계산
# 성과지표 "일별"을 기준으로 산출
# 1. 누적 수익률 그래프
# 2. 총 누적 수익률
# 3. 연복리 수익률(CAGR)
# 4. 샤프비율
# 5. MDD
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 

csv_test = pd.read_csv('./data/aggressive/data_daily/BND ETF Stock Price History_daily.csv')

print(csv_test)