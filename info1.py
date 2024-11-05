from pybit.unified_trading import HTTP
import pandas as pd
import ta

# 1. 바이비트 퍼블릭 API에서 데이터 가져오기
session = HTTP()
response = session.get_kline(symbol="BTCUSDT", interval="5", limit=200)

# API 응답 구조 출력
print("API response structure:", response)

# 데이터가 비어있을 경우 처리
data = response.get('result', [])
if not data:
    raise ValueError("데이터를 가져오지 못했습니다. API 응답을 확인하세요.")

# 2. 데이터프레임으로 변환
df = pd.DataFrame(data)
print("Data columns:", df.columns)  # 데이터의 열 확인

# 'start_time' 또는 'timestamp' 열을 기준으로 날짜 변환 및 인덱스로 설정
time_column = None
if 'start_time' in df.columns:
    time_column = 'start_time'
elif 'timestamp' in df.columns:
    time_column = 'timestamp'
elif 'time' in df.columns:
    time_column = 'time'  # Trying another potential column name based on the error

if time_column:
    df['start_at'] = pd.to_datetime(df[time_column], unit='s')
    df.set_index('start_at', inplace=True)
else:
    raise KeyError("Time column ('start_time', 'timestamp', or 'time') not found in the data.")

# Convert relevant columns to float and handle missing data
df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)

# 3. 기술적 지표 계산 (ta 라이브러리 사용)
try:
    # RSI 계산
    df['rsi'] = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi()
    # EMA(20) 계산
    df['ema_20'] = ta.trend.EMAIndicator(close=df['close'], window=20).ema_indicator()
    # 볼린저 밴드 계산
    bb = ta.volatility.BollingerBands(close=df['close'], window=20)
    df['bb_upper'] = bb.bollinger_hband()
    df['bb_lower'] = bb.bollinger_lband()
except Exception as e:
    raise RuntimeError(f"기술적 지표 계산 중 오류가 발생했습니다: {e}")

# 4. 결과 출력
print(df.tail())
