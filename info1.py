from pybit import HTTP
import pandas as pd
import ta

# 1. 바이비트 퍼블릭 API에서 데이터 가져오기
session = HTTP("https://api.bybit.com")
response = session.query_kline(
    symbol="BTCUSDT",  # BTC/USDT 페어
    interval="5",      # 5분 봉 데이터
    limit=200           # 최근 200개의 데이터 가져오기
)

data = response['result']

# 2. 데이터프레임으로 변환
# 'open_time', 'open', 'high', 'low', 'close', 'volume'을 포함한 DataFrame 생성
df = pd.DataFrame(data)
df['open_time'] = pd.to_datetime(df['open_time'], unit='s')
df.set_index('open_time', inplace=True)
df = df[['open', 'high', 'low', 'close', 'volume']]
df = df.astype(float)

# 3. 기술적 지표 계산하기 (ta 라이브러리 사용)
# 예: RSI, EMA, Bollinger Bands 등
df['rsi'] = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi()
df['ema_20'] = ta.trend.EMAIndicator(close=df['close'], window=20).ema_indicator()
bb = ta.volatility.BollingerBands(close=df['close'], window=20)
df['bb_upper'] = bb.bollinger_hband()
df['bb_lower'] = bb.bollinger_lband()

# 4. 결과 출력
df.tail()
