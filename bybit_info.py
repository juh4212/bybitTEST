import os
from pybit.unified_trading import HTTP

def get_api_credentials():
    """환경 변수에서 API 키와 시크릿 키를 불러옵니다."""
    api_key = os.getenv('BYBIT_API_KEY')
    api_secret = os.getenv('BYBIT_API_SECRET')
    
    if not api_key or not api_secret:
        raise EnvironmentError("BYBIT_API_KEY와 BYBIT_API_SECRET 환경 변수가 설정되어 있어야 합니다.")
    
    return api_key, api_secret

def get_wallet_balance(session, account_type="CONTRACT"):
    """계좌 잔고를 조회하는 함수"""
    try:
        response = session.get_wallet_balance(
            accountType=account_type,
        )
        print(response)  # 응답 데이터 출력

        if response['retCode'] == 0:
            balance_list = response['result']['list']
            print("Wallet Balance:")

            # balance_list가 리스트로 오는 경우, 전체 잔고와 사용 가능한 잔고를 출력합니다.
            for item in balance_list:
                if isinstance(item, dict) and item.get('coin') and isinstance(item['coin'], list) and item['coin'][0].get('coin') == 'USDT':
                    coin_info = item['coin'][0]
                    total_balance = coin_info.get('equity', 'N/A')
                    available_balance = coin_info.get('availableToWithdraw', 'N/A')
                    print(f"USDT Total Balance: {total_balance}, Available Balance: {available_balance}")
                    break
            else:
                print("No balance information found for USDT")
        else:
            print(f"Error: {response['retMsg']}")
    except Exception as e:
        print(f"An error occurred while fetching wallet balance: {e}")

def get_linear_positions(session, symbol="BTCUSDT"):
    """Linear 계약 포지션 정보를 조회하는 함수"""
    try:
        response = session.get_positions(
            category="linear",
            symbol=symbol,
        )
        print(response)  # 응답 데이터 출력

        if response['retCode'] == 0:
            positions = response.get('result', {}).get('list', [])

            if isinstance(positions, list) and len(positions) > 0:
                print("Linear Positions:")
                for pos in positions:
                    entry_price = pos.get('entryPrice', pos.get('avgPrice', 'N/A'))
                    print(f"Symbol: {pos['symbol']}, Size: {pos['size']}, Side: {pos['side']}, Entry Price: {entry_price}")
            else:
                print("No positions found")
        else:
            print(f"Error: {response['retMsg']}")
    except Exception as e:
        print(f"An error occurred while fetching linear positions: {e}")
