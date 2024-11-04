import os
import requests
import time
import hashlib
import hmac
import urllib.parse

# 환경 변수에서 API 키와 시크릿 키 불러오기
API_KEY = os.getenv('BYBIT_API_KEY')
API_SECRET = os.getenv('BYBIT_API_SECRET')

# Bybit REST API 엔드포인트
BASE_URL = 'https://api.bybit.com'

def generate_signature(secret, params):
    """Bybit API 서명 생성 함수"""
    ordered_params = urllib.parse.urlencode(sorted(params.items()))
    to_sign = ordered_params
    return hmac.new(secret.encode('utf-8'), to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

def get_wallet_balance():
    """계좌 잔고 조회 함수"""
    endpoint = '/v2/private/wallet/balance'
    url = BASE_URL + endpoint

    # 현재 타임스탬프 (밀리초)
    timestamp = int(time.time() * 1000)

    params = {
        'api_key': API_KEY,
        'timestamp': timestamp,
        'coin': 'USDT',  # 조회하고자 하는 코인
    }

    # 서명 생성
    params['sign'] = generate_signature(API_SECRET, params)

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data['ret_code'] == 0:
            balance_info = data['result']
            print("Wallet Balance:")
            for coin, info in balance_info.items():
                print(f"{coin}: {info['available_balance']} available, {info['used_margin']} used")
        else:
            print(f"Error {data['ret_code']}: {data['ret_msg']}")
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")

def get_linear_positions():
    """Linear 계약 포지션 정보 조회 함수"""
    endpoint = '/private/linear/position/list'
    url = BASE_URL + endpoint

    # 현재 타임스탬프 (밀리초)
    timestamp = int(time.time() * 1000)

    params = {
        'api_key': API_KEY,
        'timestamp': timestamp,
        'category': 'linear',  # Linear 계약 카테고리
        'is_null': False,      # 포지션이 있는 것만 조회
    }

    # 서명 생성
    params['sign'] = generate_signature(API_SECRET, params)

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data['ret_code'] == 0:
            positions = data['result']
            print("Linear Positions:")
            for pos in positions:
                print(f"Symbol: {pos['symbol']}, Size: {pos['size']}, Side: {pos['side']}, Entry Price: {pos['entry_price']}")
        else:
            print(f"Error {data['ret_code']}: {data['ret_msg']}")
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")

def main():
    print("Fetching Wallet Balance...")
    get_wallet_balance()
    print("\nFetching Linear Positions...")
    get_linear_positions()

if __name__ == "__main__":
    # API 키와 시크릿 키가 설정되어 있는지 확인
    if not API_KEY or not API_SECRET:
        print("Error: BYBIT_API_KEY and BYBIT_API_SECRET environment variables must be set.")
    else:
        main()
