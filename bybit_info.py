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

def place_order(session, symbol="BTCUSDT", qty=0.001, leverage=5, marginType="ISOLATED"):
    """Linear 계약 포지션을 진입하는 함수 (헷지모드 Buy side, 레버리지 5배, 마켓 가격으로)"""
    try:
        # 레버리지 설정
        response = session.set_leverage(
            category="linear",
            symbol=symbol,
            buyLeverage=leverage,
            sellLeverage=leverage
        )
            category="linear",
            symbol=symbol,
            buyLeverage=leverage,
            sellLeverage=leverage,
        )
        if response['retCode'] != 0:
            print(f"Error setting leverage: {response['retMsg']}")
            return
        # 마진 유형 설정
        response = session.set_margin_type(
            category="linear",
            symbol=symbol,
            marginType=marginType)
        if response['retCode'] != 0:
            print(f"Error setting margin type: {response['retMsg']}")
            return

        # 주문 전 포지션 확인
        positions_response = session.get_positions(
            category="linear",
            symbol=symbol,
        )
        if positions_response['retCode'] == 0:
            positions = positions_response.get('result', {}).get('list', [])
            for pos in positions:
                if pos['side'] == 'Buy' and float(pos['size']) > 0:
                    print("Existing Buy position found, not placing a new order.")
                    return
        else:
            print(f"Error checking positions: {positions_response['retMsg']}")
            return

        response = session.place_order(
            category="linear",
            symbol=symbol,
            side="Buy",
            orderType="MARKET",  # 주문 유형을 대문자로 수정
            qty=str(qty),
            timeInForce="IOC",  # GTC 대신 IOC (Immediate Or Cancel) 사용
              # 레버리지 설정 변경
            positionIdx=1,  # hedge-mode Buy side
        )
        print(response)  # 주문 응답 출력
        if response['retCode'] == 0:
            print("Order placed successfully.")
        else:
            print(f"Error placing order: {response['retMsg']}")
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
        testnet=False,  # 테스트넷을 사용하려면 True로 설정
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
