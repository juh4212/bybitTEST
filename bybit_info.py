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

def place_order(session, symbol="BTCUSDT", qty="0.001", leverage=5):
    """Linear 계약에 레버리지 5배로 BTCUSDT Market Buy 주문을 제출합니다."""
    try:
        # 레버리지 설정
        response_leverage = session.set_leverage(
            category="linear",
            symbol=symbol,
            buyLeverage=leverage,
            sellLeverage=leverage
        )
        print(response_leverage)

        if response_leverage['retCode'] != 0:
            print(f"레버리지 설정 실패: {response_leverage['retMsg']}")
            return

        # 주문 제출
        response_order = session.place_order(
            category="linear",
            symbol=symbol,
            side="Buy",
            orderType="Market",
            qty=qty,
            positionIdx=1,  # 헷지 모드 Buy 포지션
            timeInForce="IOC"  # 즉시 체결 혹은 취소
        )
        print(response_order)

        if response_order['retCode'] == 0:
            print(f"주문 성공: 주문 ID {response_order['result']['orderId']}")
        else:
            print(f"주문 실패: {response_order['retMsg']}")
    except Exception as e:
        print(f"An error occurred while placing the order: {e}")

def main():
    try:
        api_key, api_secret = get_api_credentials()
    except EnvironmentError as e:
        print(e)
        return
    
    # Bybit 세션 생성 (testnet=False로 설정하여 메인넷 사용)
    session = HTTP(
        testnet=True,  # 테스트넷을 사용하려면 True로 설정
        api_key=api_key,
        api_secret=api_secret,
    )
    
    print("Fetching Wallet Balance...")
    get_wallet_balance(session)
    
    print("\nFetching Linear Positions...")
    get_linear_positions(session)
    
    print("\nPlacing Order...")
    place_order(session)

if __name__ == "__main__":
    main()
