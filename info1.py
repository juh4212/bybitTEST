from pybit.unified_trading import HTTP
import pandas as pd
import time
import ta  # ta 라이브러리 사용

# Bybit API 세션 생성
session = HTTP()

# 현재 시간의 Unix timestamp (밀리초 단위)
current_time_ms = int(time.time() * 1000)

# 7일 전의 Unix timestamp 계산 (168시간 * 3600초 * 1000밀리초)
start_time_ms = current_time_ms - (168 * 3600 * 1000)

# 1시간 간격의 7일치 데이터 가져오기 (168개 캔들)
response = session.get_kline(symbol="BTCUSDT", interval="60", limit=168, from_time=start_time_ms)
data = response.get('result', [])

# 데이터가 비어있을 경우 처리
if not data:
    raise ValueError("데이터를 가져오지 못했습니다. API 응답을 확인하세요.")

# 데이터프레임으로 변환 및 열 이름 확인
df = pd.DataFrame(data)
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

# 보조지표 추가 (ta 라이브러리 사용)
# 20기간 단순 이동 평균 (SMA) 추가
df_hourly['SMA_20'] = ta.trend.sma_indicator(df_hourly['close'], window=20)

# 50기간 지수 이동 평균 (EMA) 추가
df_hourly['EMA_50'] = ta.trend.ema_indicator(df_hourly['close'], window=50)

# 14기간 상대강도지수 (RSI) 추가
df_hourly['RSI_14'] = ta.momentum.rsi(df_hourly['close'], window=14)

# NaN 값 제거 (보조지표 계산 후 초기 몇 개 행에 NaN이 있을 수 있음)
df_hourly = df_hourly.dropna()

# 결과 출력
print(df_hourly.tail())
print(f"총 데이터 포인트 수: {len(df_hourly)}")
