from pybit.unified_trading import HTTP
import pandas as pd
import ta

# 1. Bybit API에서 데이터 가져오기
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
print("데이터 열 확인:", df.columns)  # 데이터의 열 확인

# 'list' 열의 구조를 확인하여 데이터가 있는지 확인
if 'list' not in df.columns:
    raise KeyError("'list' 열이 데이터에 없습니다. API 응답 구조를 확인하세요.")

# 'list' 열의 내용 확인
print("list 열 내용:", df['list'].head())

# 'list' 열을 확장하여 개별 열로 변환
data_expanded = pd.DataFrame(df['list'].tolist(), columns=['start_time', 'open', 'high', 'low', 'close', 'volume', 'other_column_1', 'other_column_2'])

# 'start_time' 열을 datetime 형식으로 변환하고 인덱스로 설정
data_expanded['start_at'] = pd.to_datetime(data_expanded['start_time'], unit='s')
data_expanded.set_index('start_at', inplace=True)

# 필요한 열만 선택하고 데이터 타입을 float으로 변환
df = data_expanded[['open', 'high', 'low', 'close', 'volume']].astype(float)

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
