from pybit.unified_trading import HTTP
import pandas as pd
import ta

# Bybit API 세션 생성
session = HTTP()

# 1시간 간격의 7일치 데이터 가져오기 (168개 캔들)
response = session.get_kline(symbol="BTCUSDT", interval="60", limit=168)
data = response.get('result', [])

# 데이터프레임으로 변환
df_hourly = pd.DataFrame(data)

# 'start_time'을 datetime 형식으로 변환하고 인덱스로 설정 (밀리초 단위인 경우 'unit'을 'ms'로 설정)
df_hourly['start_at'] = pd.to_datetime(df_hourly['start_time'], unit='ms')
df_hourly.set_index('start_at', inplace=True)

# 필요한 열만 선택하고 데이터 타입을 float으로 변환
df_hourly = df_hourly[['open', 'high', 'low', 'close', 'volume']].astype(float)

# NaN 값 제거
df_hourly = df_hourly.dropna()

# 지표 추가 (예시로 볼린저 밴드만 추가)
bb = ta.volatility.BollingerBands(close=df_hourly['close'], window=20)
df_hourly['bb_upper'] = bb.bollinger_hband()
df_hourly['bb_lower'] = bb.bollinger_lband()

# 결과 출력
print(df_hourly.tail())
