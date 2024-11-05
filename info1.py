from pybit.unified_trading import HTTP
import pandas as pd
from datetime import datetime, timedelta

# Bybit API 세션 생성
session = HTTP()

# 현재 시간 기준으로 7일 전 시간 설정
end_time = int(datetime.now().timestamp())  # 현재 시간을 초 단위로 변환
seven_days_ago = end_time - 7 * 24 * 60 * 60  # 7일 전 시간 (초 단위)

# 데이터를 저장할 리스트
all_data = []

# 데이터를 반복적으로 가져와 7일(168시간) 이상의 데이터를 확보
while len(all_data) < 168:
    response = session.get_kline(symbol="BTCUSDT", interval="60", limit=200, **{"from": seven_days_ago})
    data = response.get('result', [])
    
    # 데이터가 비어 있으면 반복 종료
    if not data:
        print("더 이상 데이터가 없습니다.")
        break

    # 데이터를 리스트에 추가
    all_data.extend(data)

    # 마지막 데이터의 시간으로 seven_days_ago 업데이트
    seven_days_ago = data[-1][0]  # 마지막 데이터의 시간을 기준으로 다음 요청 설정
    seven_days_ago += 1  # 다음 요청 시 중복 방지를 위해 1초 추가

# 데이터프레임으로 변환
df = pd.DataFrame(all_data, columns=['start_time', 'open', 'high', 'low', 'close', 'volume', 'turnover'])

# 'start_time'을 datetime 형식으로 변환하고 인덱스로 설정
df['start_at'] = pd.to_datetime(df['start_time'], unit='s')
df.set_index('start_at', inplace=True)

# 필요한 열만 선택하고 데이터 타입을 float으로 변환
df_hourly = df[['open', 'high', 'low', 'close', 'volume']].astype(float)

# 결과 출력 (마지막 5개 행)
print(df_hourly.tail())
