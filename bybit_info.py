import os
import pandas as pd
import numpy as np
import ta
from pybit.unified_trading import HTTP

def get_api_credentials():
    """환경 변수에서 API 키와 시크릿 키를 불러옵니다."""
    api_key = os.getenv('BYBIT_API_KEY')
    api_secret = os.getenv('BYBIT_API_SECRET')
    
    if not api_key or not api_secret:
        raise EnvironmentError("BYBIT_API_KEY와 BYBIT_API_SECRET 환경 변수가 설정되어 있어야 합니다.")
    
    return api_key, api_secret

def get_historical_volatility(session, category="option", base_coin="BTC", period=30):
    """옵션의 과거 변동성을 가져오는 함수"""
    try:
        response = session.get_historical_volatility(
            category=category,
            baseCoin=base_coin,
            period=period
        )
        if response['retCode'] == 0:
            print("Historical Volatility Data:")
            print(response['result'])
        else:
            print(f"Error fetching historical volatility data: {response['retMsg']}")
    except Exception as e:
        print(f"An error occurred while fetching historical volatility: {e}")

def get_historical_data(session, symbol="BTCUSDT", interval="1h", limit=200):
    """과거 데이터를 가져오는 함수"""
    try:
        response = session.get_kline(category="linear", symbol=symbol, interval=interval, limit=limit)
        if response['retCode'] == 0:
            df = pd.DataFrame(response['result'])
            # 열의 이름을 정확하게 할당하기 위해 응답 데이터의 키 사용
            expected_columns = ['start_at', 'open', 'high', 'low', 'close', 'volume', 'turnover']
            df.columns = expected_columns[:df.shape[1]]
            df['close'] = df['close'].astype(float)
            df['open'] = df['open'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['volume'] = df['volume'].astype(float)
            return df
        else:
            print(f"Error fetching historical data: {response['retMsg']}")
            return None
    except Exception as e:
        print(f"An error occurred while fetching historical data: {e}")
        return None

def calculate_indicators(df):
    """기술적 지표를 계산하는 함수"""
    # Using TA-Lib for more indicators
    df['ema_20'] = ta.trend.ema_indicator(df['close'], window=20)
    df['ema_50'] = ta.trend.ema_indicator(df['close'], window=50)
    df['rsi'] = ta.momentum.rsi(df['close'], window=14)
    macd = ta.trend.MACD(close=df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    bb = ta.volatility.BollingerBands(close=df['close'], window=20)
    df['upper_band'] = bb.bollinger_hband()
    df['middle_band'] = bb.bollinger_mavg()
    df['lower_band'] = bb.bollinger_lband()
    df['volume_ma'] = df['volume'].rolling(window=20).mean()
    return df

def make_trade_decision(df):
    """AI 기반으로 매매 결정을 내리는 함수 (기본적인 논리만 사용)"""
    latest = df.iloc[-1]
    if latest['close'] > latest['ema_20'] and latest['macd'] > latest['macd_signal'] and latest['rsi'] < 70:
        return "Buy"
    elif latest['close'] < latest['ema_20'] and latest['macd'] < latest['macd_signal'] and latest['rsi'] > 30:
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
    
    print("\nFetching Historical Volatility...")
    get_historical_volatility(session)

if __name__ == "__main__":
    main()
