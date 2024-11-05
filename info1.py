from pybit.unified_trading import HTTP
import pandas as pd
import ta

# 1. 바이비트 퍼블릭 API에서 데이터 가져오기
session = HTTP()
response = session.get_kline(
    symbol="BTCUSDT",
    interval="5",
    limit=200
)

# Print response to inspect data structure
print("API response structure:", response)

data = response.get('result', [])

# 데이터가 비어있을 경우 처리
if not data:
    raise ValueError("데이터를 가져오지 못했습니다. API 응답을 확인하세요.")

# 2. 데이터프레임으로 변환
# Print data to inspect available columns
df = pd.DataFrame(data)
print("Data columns:", df.columns)

# Verify if 'start_time' exists in the DataFrame and convert it to datetime
if 'start_time' in df.columns:
    df['start_at'] = pd.to_datetime(df['start_time'], unit='s')
elif 'timestamp' in df.columns:
    df['start_at'] = pd.to_datetime(df['timestamp'], unit='s')
else:
    raise KeyError("Time column ('start_time' or 'timestamp') not found in the data.")

df.set_index('start_at', inplace=True)
df = df[['open', 'high', 'low', 'close', 'volume']]
df = df.astype(float)

# 3. 기술적 지표 계산하기 (ta 라이브러리 사용)
# 예: RSI, EMA, Bollinger Bands 등
try:
    df['rsi'] = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi()
    df['ema_20'] = ta.trend.EMAIndicator(close=df['close'], window=20).ema_indicator()
    bb = ta.volatility.BollingerBands(close=df['close'], window=20)
    df['bb_upper'] = bb.bollinger_hband()
    df['bb_lower'] = bb.bollinger_lband()
except Exception as e:
    raise RuntimeError(f"기술적 지표 계산 중 오류가 발생했습니다: {e}")

# 4. 결과 출력
print(df.tail())
