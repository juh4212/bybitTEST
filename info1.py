from pybit.unified_trading import HTTP
import pandas as pd
from datetime import datetime, timedelta

# Bybit API 세션 생성
session = HTTP()

# 시작 시간 설정 (7일 전 시간)
end_time = int(datetime.now().timestamp() * 1000)  # 현재 시간을 밀리초로 변환
seven_days_ago = end_time - 7 * 24 * 60 * 60 * 1000  # 7일 전

# 데이터를 저장할 리스트
all_data = []

# 데이터를 반복적으로 가져와 168개 이상의 캔들을 확보
while seven_days_ago < end_time:
    response = session.get_kline(symbol="BTCUSDT", interval="60", limit=200, **{"from": seven_days_ago // 1000})
    data = response.get('result', [])
    
    # 데이터가 비어 있으면 반복 종료
    if not data:
        print("더 이상 데이터가 없습니다.")
        break

    # 데이터를 리스트에 추가
    all_data.extend(data)

    # data가 비어 있지 않을 경우 마지막 데이터의 시간으로 seven_days_ago 업데이트
    if data:
        seven_days_ago = data[-1][0] * 1000 + 1  # 마지막 데이터의 시간을 기준으로 다음 요청 설정

# 데이터프레임으로 변환
df = pd.DataFrame(all_data)
print("데이터프레임의 열 확인:", df.columns)  # 열 이름 출력

# 'list' 열이 있는지 확인하여 확장
if 'list' not in df.columns:
    raise KeyError("'list' 열이 데이터에 없습니다. API 응답 구조를 확인하세요.")

# 'list' 열의 내용을 개별 열로 확장
columns = ['start_time', 'open', 'high', 'low', 'close', 'volume', 'turnover']
df_hourly = pd.DataFrame(df['list'].tolist(), columns=columns)

# 'start_time'을 datetime 형식으로 변환하고 인덱스로 설정 (밀리초 단위로 변환)
df_hourly['start_at'] = pd.to_datetime(df_hourly['start_time'], unit='ms')
df_hourly.set_index('start_at', inplace=True)

# 필요한 열만 선택하고 데이터 타입을 float으로 변환
df_hourly = df_hourly[['open', 'high', 'low', 'close', 'volume']].astype(float)

# NaN 값 제거
df_hourly = df_hourly.dropna()

# 결과 출력
print(df_hourly.tail())
