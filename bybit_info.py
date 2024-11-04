import os
from pybit.unified_trading import HTTP

def get_api_credentials():
    """환경 변수에서 API 키와 시크릿 키를 불러옵니다."""
    api_key = os.getenv('BYBIT_API_KEY')
    api_secret = os.getenv('BYBIT_API_SECRET')
    
    if not api_key or not api_secret:
        raise EnvironmentError("BYBIT_API_KEY와 BYBIT_API_SECRET 환경 변수가 설정되어 있어야 합니다.")
    
    return api_key, api_secret

def get_wallet_balance(session, account_type="CONTRACT", coin="USDT"):
    """계좌 잔고를 조회하는 함수"""
    try:
        response = session.get_wallet_balance(
            accountType=account_type,
            coin=coin,
        )
        if response['retMsg'] == 'OK':
            balance_info = response['result']
            print("Wallet Balance:")
            for coin, info in balance_info.items():
                print(f"{coin}: {info['availableBalance']} available, {info['usedMargin']} used")
        else:
            print(f"Error: {response['retMsg']}")
    except Exception as e:
        print(f"An error occurred while fetching wallet balance: {e}")

def get_linear_positions(session, symbol="BTCUSD"):
    """Linear 계약 포지션 정보를 조회하는 함수"""
    try:
        response = session.get_positions(
            category="linear",
            symbol=symbol,
        )
        if response['retMsg'] == 'OK':
            positions = response['result']['data']
            print("Linear Positions:")
            for pos in positions:
                print(f"Symbol: {pos['symbol']}, Size: {pos['size']}, Side: {pos['side']}, Entry Price: {pos['entryPrice']}")
        else:
            print(f"Error: {response['retMsg']}")
    except Exception as e:
        print(f"An error occurred while fetching linear positions: {e}")

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

if __name__ == "__main__":
    main()
