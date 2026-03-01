import time
import threading
from typing import Optional, List, Dict, Callable
import websocket

try:
    from websocket_functions import (
        connections,
        get_url_and_header_data,
        read_message,
        subscribe as subscribe_helper,
        unsubscribe as unsubscribe_helper,
        subscribe_option_greeks as subscribe_option_greeks_helper,
        unsubscribe_option_greeks as unsubscribe_option_greeks_helper
    )
except ImportError:
    try:
        from .websocket_functions import (
            connections,
            get_url_and_header_data,
            read_message,
            subscribe as subscribe_helper,
            unsubscribe as unsubscribe_helper,
            subscribe_option_greeks as subscribe_option_greeks_helper,
            unsubscribe_option_greeks as unsubscribe_option_greeks_helper
        )
    except ImportError as e:
        raise

class FirstockWebSocket:
    def __init__(
        self,
        tokens: Optional[List[str]] = None,
        option_greeks_tokens: Optional[List[str]] = None,
        order_data: Optional[Callable] = None,
        position_data: Optional[Callable] = None,
        subscribe_feed_data: Optional[Callable] = None,
        subscribe_option_greeks_data: Optional[Callable] = None,
        on_reconnect: Optional[Callable[[websocket.WebSocket], None]] = None 
    ):
        self.tokens = tokens or []
        self.option_greeks_tokens = option_greeks_tokens or []
        self.order_data = order_data
        self.position_data = position_data
        self.subscribe_feed_data = subscribe_feed_data
        self.subscribe_option_greeks_data = subscribe_option_greeks_data
        self.on_reconnect = on_reconnect  
    
    def to_dict(self):
        return {
            'tokens': self.tokens,
            'option_greeks_tokens': self.option_greeks_tokens,
            'order_data': self.order_data,
            'position_data': self.position_data,
            'subscribe_feed_data': self.subscribe_feed_data,
            'subscribe_option_greeks_data': self.subscribe_option_greeks_data,
            'on_reconnect': self.on_reconnect  
        }

class Firstock:
    
    @classmethod
    def initialize_websockets(
        cls,
        user_id: str,
        model: FirstockWebSocket,
        config: Optional[Dict] = None
    ) -> tuple:
        if config is None:
            config = {}
        config.setdefault('scheme', 'wss')
        config.setdefault('host', 'socket.firstock.in/V2')
        config.setdefault('path', '/ws')
        config.setdefault('source', 'developer-api')
        config.setdefault('accept_encoding', 'gzip, deflate, br')
        config.setdefault('accept_language', 'en-US,en;q=0.9')
        config.setdefault('origin', 'https://firstock.in')
        config.setdefault('max_websocket_connection_retries', 3)
        config.setdefault('time_interval', 5)
        
        base_url, headers, err = get_url_and_header_data(user_id, config)
        if err:
            return None, err
        
        try:
            ws = websocket.create_connection(base_url, header=headers)
            connections.add_connection(ws)
            
            msg = ws.recv()
            
            if "Authentication successful" in msg:
                time.sleep(0.5)
                
                model_dict = model.to_dict()
                thread = threading.Thread(
                    target=read_message,
                    args=(user_id, ws, model_dict, config),
                    daemon=True
                )
                thread.start()
                
                time.sleep(0.5)
                
                if model.tokens:
                    subscribe_err = subscribe_helper(ws, model.tokens)
                
                if model.option_greeks_tokens:
                    subscribe_err = subscribe_option_greeks_helper(ws, model.option_greeks_tokens)
                
                return ws, None
            elif "Maximum sessions limit" in msg:
                connections.delete_connection(ws)
                err = {
                    "error": {
                        "message": msg
                    }
                }
                return None, err
            else:
                connections.delete_connection(ws)
                err = {
                    "error": {
                        "message": f"Unexpected authentication response: {msg}"
                    }
                }
                return None, err
        except Exception as e:
            err = {
                "error": {
                    "message": str(e)
                }
            }
            return None, err
    
    @classmethod
    def close_websocket(cls, ws: Optional[websocket.WebSocket]) -> Optional[Dict]:
        if ws is None:
            return {
                "error": {
                    "message": "Connection does not exist"
                }
            }
        
        if connections.check_if_connection_exists(ws):
            try:
                ws.close()
                connections.delete_connection(ws)
                return None
            except Exception as e:
                if "closed" not in str(e).lower():
                    return {
                        "error": {
                            "message": str(e)
                        }
                    }
                else:
                    connections.delete_connection(ws)
                    return None
        else:
            return {
                "error": {
                    "message": "Connection does not exist"
                }
            }
    
    @classmethod
    def subscribe(
        cls,
        ws: Optional[websocket.WebSocket],
        tokens: List[str]
    ) -> Optional[Dict]:
        if ws is None:
            return {
                "error": {
                    "message": "Connection does not exist"
                }
            }
        
        return subscribe_helper(ws, tokens)
    
    @classmethod
    def unsubscribe(
        cls,
        ws: Optional[websocket.WebSocket],
        tokens: List[str]
    ) -> Optional[Dict]:
        if ws is None:
            return {
                "error": {
                    "message": "Connection does not exist"
                }
            }
        
        return unsubscribe_helper(ws, tokens)
    
    @classmethod
    def subscribe_option_greeks(
        cls,
        ws: Optional[websocket.WebSocket],
        tokens: List[str]
    ) -> Optional[Dict]:
        if ws is None:
            return {
                "error": {
                    "message": "Connection does not exist"
                }
            }
        
        return subscribe_option_greeks_helper(ws, tokens)
    
    @classmethod
    def unsubscribe_option_greeks(
        cls,
        ws: Optional[websocket.WebSocket],
        tokens: List[str]
    ) -> Optional[Dict]:
        if ws is None:
            return {
                "error": {
                    "message": "Connection does not exist"
                }
            }
        
        return unsubscribe_option_greeks_helper(ws, tokens)