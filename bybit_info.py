import os
import pandas as pd
import numpy as np
from pybit.unified_trading import HTTP

def get_api_credentials():
    """환경 변수에서 API 키와 시크릿 키를 불러옵니다."""
    api_key = os.getenv('BYBIT_API_KEY')
    api_secret = os.getenv('BYBIT_API_SECRET')
    
    if not api_key or not api_secret:
        raise EnvironmentError("BYBIT_API_KEY와 BYBIT_API_SECRET 환경 변수가 설정되어 있어야 합니다.")
    
    return api_key, api_secret

def get_historical_data(session, symbol="BTCUSDT", interval="1h", limit=200):
    """과거 데이터를 가져오는 함수"""
    try:
        response = session.get_kline(category="linear", symbol=symbol, interval=interval, limit=limit)
        if response['retCode'] == 0:
            df = pd.DataFrame(response['result'])
            df.columns = ['start_at', 'open', 'high', 'low', 'close', 'volume']
            return df
        else:
            print(f"Error fetching historical data: {response['retMsg']}")
            return None
    except Exception as e:
        print(f"An error occurred while fetching historical data: {e}")
        return None

def calculate_indicators(df):
    """기술적 지표를 계산하는 함수"""
    df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
    df['rsi'] = calculate_rsi(df['close'])
    df['macd'], df['signal_line'] = calculate_macd(df['close'])
    df['upper_band'], df['middle_band'], df['lower_band'] = calculate_bollinger_bands(df['close'])
    df['fibonacci_retracement'] = calculate_fibonacci_retracement(df['close'])
    df['volume_ma'] = df['volume'].rolling(window=20).mean()
    # 일목균형표 계산 생략 (복잡도 증가 방지, 필요시 추가 가능)
    return df

def calculate_rsi(series, period=14):
    """RSI를 계산하는 함수"""
    delta = series.diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(series, short_period=12, long_period=26, signal_period=9):
    """MACD를 계산하는 함수"""
    short_ema = series.ewm(span=short_period, adjust=False).mean()
    long_ema = series.ewm(span=long_period, adjust=False).mean()
    macd = short_ema - long_ema
    signal_line = macd.ewm(span=signal_period, adjust=False).mean()
    return macd, signal_line

def calculate_bollinger_bands(series, period=20, num_std_dev=2):
    """볼린저 밴드를 계산하는 함수"""
    middle_band = series.rolling(window=period).mean()
    std_dev = series.rolling(window=period).std()
    upper_band = middle_band + (std_dev * num_std_dev)
    lower_band = middle_band - (std_dev * num_std_dev)
    return upper_band, middle_band, lower_band

def calculate_fibonacci_retracement(series):
    """피보나치 되돌림 계산 (단순 예시)"""
    max_price = series.max()
    min_price = series.min()
    retracement_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
    return [(max_price - min_price) * level + min_price for level in retracement_levels]

def make_trade_decision(df):
    """AI 기반으로 매매 결정을 내리는 함수 (기본적인 논리만 사용)"""
    latest = df.iloc[-1]
    if latest['close'] > latest['ema_20'] and latest['macd'] > latest['signal_line'] and latest['rsi'] < 70:
        return "Buy"
    elif latest['close'] < latest['ema_20'] and latest['macd'] < latest['signal_line'] and latest['rsi'] > 30:
        return "Sell"
    return "Hold"

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

def place_order(session, symbol="BTCUSDT", qty="0.001", leverage=5, side="Buy"):
    """Linear 계약에 레버리지 5배로 BTCUSDT 주문을 제출합니다."""
    try:
        # 레버리지를 설정하기 전에 현재 레버리지 값을 확인
        current_positions = session.get_positions(category="linear", symbol=symbol)
        current_leverage = None
        if current_positions['retCode'] == 0 and len(current_positions['result']['list']) > 0:
            current_leverage = current_positions['result']['list'][0].get('leverage')
        
        if current_leverage is None or float(current_leverage) != leverage:
            response_leverage = session.set_leverage(
                category="linear",
                symbol=symbol,
                buyLeverage=str(leverage),
                sellLeverage=str(leverage)
            )
            if response_leverage['retCode'] != 0:
                print(f"레버리지 설정 실패: {response_leverage['retMsg']}")
                return

        # 주문 제출
        response_order = session.place_order(
            category="linear",
            symbol=symbol,
            side=side,
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
        testnet=False,  # 테스트넷을 사용하려면 True로 설정
        api_key=api_key,
        api_secret=api_secret,
    )
    
    print("Fetching Wallet Balance...")
    get_wallet_balance(session)
    
    print("\nFetching Linear Positions...")
    get_linear_positions(session)
    
    print("\nFetching Historical Data...")
    df = get_historical_data(session)
    if df is not None:
        df = calculate_indicators(df)
        decision = make_trade_decision(df)
        print(f"Trade Decision: {decision}")
        if decision in ["Buy", "Sell"]:
            place_order(session, side=decision)

if __name__ == "__main__":
    main()
