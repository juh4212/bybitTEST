from pybit.unified_trading import HTTP
import pandas as pd
import ta

# 1. 바이비트 퍼블릭 API에서 데이터 가져오기
session = HTTP()
response = session.market_history.kline(
    category="linear",
    symbol="BTCUSDT",
    interval="5",
    limit=200
)

data = response.get('result', [])

# 데이터가 비어있을 경우 처리
if not data:
    raise ValueError("데이터를 가져오지 못했습니다. API 응답을 확인하세요.")

# 2. 데이터프레임으로 변환
# 'open_time', 'open', 'high', 'low', 'close', 'volume'을 포함한 DataFrame 생성
df = pd.DataFrame(data)
df['open_time'] = pd.to_datetime(df['open_time'], unit='s')
df.set_index('open_time', inplace=True)
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
