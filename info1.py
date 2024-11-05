from pybit.unified_trading import HTTP
import pandas as pd

# Bybit API 세션 생성
session = HTTP()

# 1시간 간격의 7일치 데이터 가져오기 (168개 캔들)
response = session.get_kline(symbol="BTCUSDT", interval="60", limit=168)
data = response.get('result', [])

# 데이터가 비어있을 경우 처리
if not data:
    raise ValueError("데이터를 가져오지 못했습니다. API 응답을 확인하세요.")

# 데이터프레임으로 변환 및 열 이름 확인
df_hourly = pd.DataFrame(data)
print("데이터프레임의 열 확인:", df_hourly.columns)  # 열 이름 출력

# 'start_time'이 있는지 확인하고 변환
if 'start_time' in df_hourly.columns:
    # 'start_time' 열이 있는 경우, datetime 형식으로 변환하여 인덱스로 설정
    df_hourly['start_at'] = pd.to_datetime(df_hourly['start_time'], unit='ms')
elif 'timestamp' in df_hourly.columns:
    # 'timestamp' 열이 있는 경우, datetime 형식으로 변환하여 인덱스로 설정
    df_hourly['start_at'] = pd.to_datetime(df_hourly['timestamp'], unit='ms')
else:
    raise KeyError("시간 관련 열('start_time' 또는 'timestamp')을 찾을 수 없습니다. API 응답 형식을 확인하세요.")

# 'start_at'을 인덱스로 설정
df_hourly.set_index('start_at', inplace=True)

# 필요한 열만 선택하고 데이터 타입을 float으로 변환
df_hourly = df_hourly[['open', 'high', 'low', 'close', 'volume']].astype(float)

# NaN 값 제거
df_hourly = df_hourly.dropna()

# 결과 출력
print(df_hourly.tail())
