import logging
import time
import sys
from pathlib import Path
from typing import Dict, Any

current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from websockets import Firstock, FirstockWebSocket
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Current directory: {current_dir}")
    print(f"Python path: {sys.path}")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def subscribe_feed_data(data: Dict[str, Any]):
    with open("websocket.log", "a") as log_file:
        log_file.write(f"{data}\n")
    print(data)

def subscribe_option_greeks_data(data: Dict[str, Any]):
    """Callback for option Greeks updates"""
    try:
        with open("option_greeks.log", "a") as log_file:
            log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {data}\n")
    except Exception as e:
        print(f"Error writing option Greeks: {e}")

def order_book_data(data: Dict[str, str]):
    try:
        with open("order_detail.log", "a") as log_file:
            log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {data}\n")
    except Exception as e:
        print(f"Error opening log file: {e}")


def position_book_data(data: Dict[str, Any]):
    try:
        with open("position_detail.log", "a") as log_file:
            log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {data}\n")
    except Exception as e:
        print(f"Error opening log file: {e}")


def subscribe_feed_data_2(data: Dict[str, Any]):
    try:
        with open("websocket2.log", "a") as log_file:
            log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {data}\n")
    except Exception as e:
        print(f"Error opening log file: {e}")


def subscribe_feed_data_3(data: Dict[str, Any]):
    try:
        with open("websocket3.log", "a") as log_file:
            log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {data}\n")
    except Exception as e:
        print(f"Error opening log file: {e}")

def subscribe_feed_data_4(data: Dict[str, Any]):
    try:
        with open("websocket4.log", "a") as log_file:
            log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {data}\n")
    except Exception as e:
        print(f"Error opening log file: {e}")


def main():
    user_id = 'CM2096'
    
    # No config needed - handled internally
    # Or pass minimal overrides only:
    # config = {'host': 'custom.host.com'}  # optional
    connection_ref = {'conn': None}
    
    def on_reconnect_callback(new_ws):
        """Called when connection is reconnected"""
        print(f" Connection reference updated")
        connection_ref['conn'] = new_ws

    model = FirstockWebSocket(
        tokens=[],
        option_greeks_tokens=[],
        order_data=order_book_data,
        position_data=position_book_data,
        subscribe_feed_data=subscribe_feed_data,
        subscribe_option_greeks_data=subscribe_option_greeks_data,
        on_reconnect=on_reconnect_callback
    )
    
    # Use class method directly
    conn, err = Firstock.initialize_websockets(user_id, model)
    connection_ref['conn'] = conn
    print("Error:", err)
    
    if err:
        print(f"Connection failed: {err}")
        return
    else:
        print("WebSocket connected successfully!")
    
    # # Subscribe to tokens
    err = Firstock.subscribe(connection_ref['conn'], ["BSE:500470|NSE:26000"])
    print("Error:", err)
    model = FirstockWebSocket(
        tokens=[],
        order_data=order_book_data,
        position_data=position_book_data,
        subscribe_feed_data=subscribe_feed_data
    )

        # Subscribe to option Greeks
    # err = Firstock.subscribe_option_greeks(connection_ref['conn'], ["NFO:44297"])
    # print("Option Greeks Subscribe Error:", err)
    
    # # # Later, unsubscribe
    # time.sleep(30)
    # err = Firstock.unsubscribe_option_greeks(connection_ref['conn'], ["NFO:44283"])
    # print("Option Greeks Unsubscribe Error:", err)
    
    # Uncomment for multiple connections
    # model2 = FirstockWebSocket(
    #     tokens=[],
    #     order_data=None,
    #     position_data=None,
    #     subscribe_feed_data=subscribe_feed_data_2
    # )
    
    # model3 = FirstockWebSocket(
    #     tokens=[],
    #     order_data=None,
    #     position_data=None,
    #     subscribe_feed_data=subscribe_feed_data_3
    # )

    # model4 = FirstockWebSocket(
    #     tokens=[],
    #     order_data=None,
    #     position_data=None,
    #     subscribe_feed_data=subscribe_feed_data_4
    # )
    
    
    # # Multiple connections example (uncommented to use)
    # conn2, err = Firstock.initialize_websockets(user_id, model2)
    # print("Error:", err)
    # err = Firstock.subscribe(conn2, ["BSE:1"])
    # print("Error:", err)
    
    # conn3, err = Firstock.initialize_websockets(user_id, model3)
    # print("Error:", err)
    # err = Firstock.subscribe(conn3, ["NSE:26000|BSE:1"])
    # print("Error:", err)

    # conn4, err = Firstock.initialize_websockets(user_id, model4)
    # print("Error:", err)
    # err = Firstock.subscribe(conn4, ["NSE:26000"])
    # print("Error:", err)
    
    # Test duplicate connection
    # _, err = Firstock.initialize_websockets(user_id, model)
    # print("Error:", err)
    
    # Wait for 25 seconds
    # time.sleep(25)
    
    # # Unsubscribe example
    # err = Firstock.unsubscribe(connection_ref['conn'], ["BSE:500470|NSE:26000"])
    # print("Error:", err)
    
    # Wait for 25 seconds
    time.sleep(25)
    
    # Close WebSocket connection
    err = Firstock.close_websocket(connection_ref['conn'])
    print("Close Error:", err)
    
    # Close additional connections
    # err = Firstock.close_websocket(conn2)
    # print("Close Error:", err)
    
    # err = Firstock.close_websocket(conn3)
    # print("Close Error:", err)
    
    # Keep program running (equivalent to select{} in Go)
    try:
        print("WebSocket test running. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")
        if conn:
            Firstock.close_websocket(connection_ref['conn'])


if __name__ == "__main__":
    main()

