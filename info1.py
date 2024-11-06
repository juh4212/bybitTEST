from pybit.unified_trading import HTTP
import pandas as pd
import time
import ta  # ta 라이브러리 사용
import os
from openai import OpenAI
from dotenv import load_dotenv  # 환경 변수를 로드하기 위한 라이브러리

# 환경 변수 로드 (.env 파일에서 OPENAI_API_KEY 가져오기)
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# OpenAI API 클라이언트 생성
client = OpenAI(api_key=api_key)

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
    raise ValueError("Data retrieval failed. Please check API response.")

# 데이터프레임으로 변환 및 열 이름 확인
df = pd.DataFrame(data)
print("Columns in dataframe:", df.columns)  # 열 이름 출력

# 'list' 열이 있는지 확인하여 확장
if 'list' not in df.columns:
    raise KeyError("'list' column is missing in the data. Check API response structure.")

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
df_hourly['SMA_20'] = ta.trend.sma_indicator(df_hourly['close'], window=20)
df_hourly['EMA_50'] = ta.trend.ema_indicator(df_hourly['close'], window=50)
df_hourly['RSI_14'] = ta.momentum.rsi(df_hourly['close'], window=14)

# MACD (이동 평균 수렴·확산)
df_hourly['MACD'] = ta.trend.macd(df_hourly['close'])
df_hourly['MACD_signal'] = ta.trend.macd_signal(df_hourly['close'])
df_hourly['MACD_hist'] = ta.trend.macd_diff(df_hourly['close'])

# Ichimoku Cloud (이치모쿠 구름대)
df_hourly['ichimoku_conversion'] = ta.trend.ichimoku_conversion_line(df_hourly['high'], df_hourly['low'])
df_hourly['ichimoku_base'] = ta.trend.ichimoku_base_line(df_hourly['high'], df_hourly['low'])
df_hourly['ichimoku_span_a'] = ta.trend.ichimoku_a(df_hourly['high'], df_hourly['low'])
df_hourly['ichimoku_span_b'] = ta.trend.ichimoku_b(df_hourly['high'], df_hourly['low'])

# 피보나치 되돌림 레벨 계산 (최근 고점과 저점을 기준으로 함)
recent_high = df_hourly['high'].max()
recent_low = df입), "close long" (롱 청산), "close short" (숏 청산) 또는 "hold" (관망),
  "percentage": 추천 퍼센트 (정수로 표시),
  "reason": 기술적 지표에 기반한 간결한 한국어 설명
}}

예시 응답:
1. {{
  "decision": "open long",
  "percentage": 50,
  "reason": "RSI와 EMA가 상승 추세를 나타내고 있어 매수 포지션 진입이 유리할 것으로 보입니다."
}}
2. {{
  "decision": "open short",
  "percentage": 30,
  "reason": "RSI가 과매수 상태에 가까워져 하락 가능성이 커졌으므로 매도 포지션을 추천합니다."
}}
3. {{
  "decision": "hold",
  "percentage": 0,
  "reason": "포지션 진입이 애매한 상황이며, 추세가 불확실하여 관망이 적절해 보입니다."
}}
4. {{
  "decision": "close long",
  "percentage": -30,
  "reason": "롱 포지션을 보유 중인 상황에서 일부 이익 실현을 하거나 리스크 관리를 위해 포지션을 줄이는 것이 좋습니다."
}}
5. {{
  "decision": "close short",
  "percentage": -30,
  "reason": "숏 포지션을 보유 중인 상황에서 일부 이익 실현을 하거나 시장 변동성에 대비해 리스크를 줄이는 것이 좋습니다."
}}
"""

# ChatGPT API 호출 (`gpt-4o` 모델 사용)
response = client.chat.completions.create(
    messages=[
        {"role": "user", "content": message}
    ],
    model="gpt-4o",
)

# ChatGPT의 응답 추출
chatgpt_response = response.choices[0].message.content.strip()
print("ChatGPT Response:", chatgpt_response)
