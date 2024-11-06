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

# 현재 시간의 Unix timestamp (초 단위)
current_time = int(time.time())

# 7일 전의 Unix timestamp 계산 (7일 * 24시간 * 3600초)
start_time = current_time - (7 * 24 * 3600)

# 1시간 간격의 7일치 데이터 가져오기 (168개 캔들)
response = session.get_kline(
    symbol="BTCUSDT",
    interval="60",
    limit=200,  # 여유롭게 데이터를 가져옵니다.
    from_time=start_time
)
data = response.get('result', [])

# 데이터가 비어있을 경우 처리
if not data:
    raise ValueError("Data retrieval failed. Please check API response.")

# 데이터프레임으로 변환
df = pd.DataFrame(data)

# 필요한 열 선택 및 데이터 타입 변환
df = df[['open_time', 'open', 'high', 'low', 'close', 'volume']]
df['open_time'] = pd.to_datetime(df['open_time'], unit='s')
df.set_index('open_time', inplace=True)
df = df.astype(float)

# NaN 값 제거
df = df.dropna()

# 이동 평균 계산
ma1_length = 50
ma2_length = 200
df['ma1'] = df['close'].rolling(window=ma1_length).mean()
df['ma2'] = df['close'].rolling(window=ma2_length).mean()

# Three White Soldiers 패턴 인식 함수
def three_white_soldiers(data):
    condition = (
        (data['close'] > data['open']) &
        (data['close'].shift(1) > data['open'].shift(1)) &
        (data['close'].shift(2) > data['open'].shift(2)) &
        (data['open'].shift(1) <= data['close'].shift(2)) &
        (data['close'].shift(1) > data['close'].shift(2)) &
        (data['open'] <= data['close'].shift(1)) &
        (data['close'] > data['close'].shift(1))
    )
    return condition

# Three Black Crows 패턴 인식 함수
def three_black_crows(data):
    condition = (
        (data['close'] < data['open']) &
        (data['close'].shift(1) < data['open'].shift(1)) &
        (data['close'].shift(2) < data['open'].shift(2)) &
        (data['open'].shift(1) >= data['close'].shift(2)) &
        (data['close'].shift(1) < data['close'].shift(2)) &
        (data['open'] >= data['close'].shift(1)) &
        (data['close'] < data['close'].shift(1))
    )
    return condition

# 신호 생성
df['buy_signal'] = False
df['sell_signal'] = False

# 쿨다운 기간 설정
use_cooldown = True
cooldown_period = 150  # 캔들 수

# 최근 신호 시점 추적 변수
last_buy_index = None
last_sell_index = None

# 마지막 매매 상태 추적 변수
last_was_buy = False
last_was_sell = False

# 데이터 순회하며 신호 생성
for idx in range(2, len(df)):
    cooldown_buy_condition = True
    cooldown_sell_condition = True

    if use_cooldown:
        if last_buy_index is not None:
            cooldown_buy_condition = (idx - last_buy_index) > cooldown_period
        if last_sell_index is not None:
            cooldown_sell_condition = (idx - last_sell_index) > cooldown_period

    # 매수 신호 조건
    buy_cond = (
        three_white_soldiers(df.iloc[idx-2:idx+1])[-1] and
        not last_was_buy and
        df['close'].iloc[idx] > df['ma1'].iloc[idx] and
        df['close'].iloc[idx] > df['ma2'].iloc[idx] and
        cooldown_buy_condition
    )

    # 매도 신호 조건
    sell_cond = (
        three_black_crows(df.iloc[idx-2:idx+1])[-1] and
        not last_was_sell and
        df['close'].iloc[idx] < df['ma1'].iloc[idx] and
        df['close'].iloc[idx] < df['ma2'].iloc[idx] and
        cooldown_sell_condition
    )

    if buy_cond:
        df['buy_signal'].iloc[idx] = True
        last_was_buy = True
        last_was_sell = False
        last_buy_index = idx
    elif sell_cond:
        df['sell_signal'].iloc[idx] = True
        last_was_sell = True
        last_was_buy = False
        last_sell_index = idx

# 가장 최근 데이터 추출
latest_data = df.iloc[-1]

# 현재 포지션 결정
if latest_data['buy_signal']:
    decision = "open long"
    percentage = 100  # 예시로 100%로 설정
    reason = "Three White Soldiers 패턴과 이동 평균 상향 돌파로 매수 신호 발생"
elif latest_data['sell_signal']:
    decision = "open short"
    percentage = 100
    reason = "Three Black Crows 패턴과 이동 평균 하향 돌파로 매도 신호 발생"
else:
    decision = "hold"
    percentage = 0
    reason = "특별한 매매 신호가 없어 관망 유지"

# ChatGPT 요청 메시지 작성
message = f"""
현재 시장 지표는 다음과 같습니다:
- 종가: {latest_data['close']}
- MA1 ({ma1_length}): {latest_data['ma1']}
- MA2 ({ma2_length}): {latest_data['ma2']}
- 최근 매수 신호: {latest_data['buy_signal']}
- 최근 매도 신호: {latest_data['sell_signal']}

이 지표를 바탕으로 다음 형식으로 매매 포지션을 결정해 주세요:
{{
  "decision": "{decision}",
  "percentage": {percentage},
  "reason": "{reason}"
}}
"""

# ChatGPT API 호출 (`gpt-4` 모델 사용)
response = client.chat.completions.create(
    messages=[
        {"role": "user", "content": message}
    ],
    model="gpt-4",
)

# ChatGPT의 응답 추출
chatgpt_response = response.choices[0].message.content.strip()
print("ChatGPT Response:", chatgpt_response)
