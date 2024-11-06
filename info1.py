from pybit.unified_trading import HTTP
import pandas as pd
import time
import talib as ta

# Bybit API 세션 생성
session = HTTP()

# 현재 시간의 Unix timestamp (밀리초 단위)
current_time_ms = int(time.time() * 1000)

# 7일 전의 Unix timestamp 계산 (168시간 * 3600초 * 1000밀리초)
start_time_ms = current_time_ms - (168 * 3600 * 1000)

# API에서 7일치 1시간 간격의 데이터 가져오기 (168개 캔들)
response = session.get("/v5/market/kline", params={
    "symbol": "BTCUSDT",
    "interval": "60",
    "limit": 168,
    "from": start_time_ms
})

# 응답 데이터에서 필요한 부분 추출
data = response.get('result', [])

# 데이터가 비어있을 경우 처리
if not data:
    raise ValueError("데이터를 가져오지 못했습니다. API 응답을 확인하세요.")

# 데이터프레임으로 변환 및 열 이름 확인
df = pd.DataFrame(data)

# 열 이름이 예상과 다른 경우 확인용 출력
print("데이터프레임의 열 확인:", df.columns)

# 타임스탬프를 datetime 형식으로 변환하여 인덱스로 설정
df['start_at'] = pd.to_datetime(df['startTime'], unit='ms')
df.set_index('start_at', inplace=True)

# 필요한 열만 선택하고 데이터 타입을 float으로 변환
df_hourly = df[['open', 'high', 'low', 'close', 'volume']].astype(float)

# NaN 값 제거
df_hourly = df_hourly.dropna()

# 보조지표 추가
# 20기간 단순 이동 평균 (SMA) 추가
df_hourly['SMA_20'] = ta.SMA(df_hourly['close'], timeperiod=20)

# 50기간 지수 이동 평균 (EMA) 추가
df_hourly['EMA_50'] = ta.EMA(df_hourly['close'], timeperiod=50)

# 14기간 상대강도지수 (RSI) 추가
df_hourly['RSI_14'] = ta.RSI(df_hourly['close'], timeperiod=14)

# NaN 값 제거 (보조지표 계산 후 초기 몇 개 행에 NaN이 있을 수 있음)
df_hourly = df_hourly.dropna()

# 결과 출력
print(df_hourly.tail())
