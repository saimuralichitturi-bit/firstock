import json
import time
from typing import Dict, List, Optional, Callable
from urllib.parse import urlencode
from enum import Enum
import websocket
import threading

class UpdateType(Enum):
    ORDER = "order"
    POSITION = "position"
    MARKET_FEED = "market_feed"
    OPTION_GREEKS = "option_greeks"

class SafeConn:
    def __init__(self, ws):
        self.ws = ws
        self.lock = threading.Lock()

class ConnectionManager:
    def __init__(self):
        self.conn_map: Dict[SafeConn, bool] = {}
        self.index_map: Dict[websocket.WebSocket, SafeConn] = {}
        self.lock = threading.Lock()

    def count_connections(self) -> int:
        with self.lock:
            return len(self.conn_map)
    
    def add_connection(self, ws: websocket.WebSocket) -> SafeConn:
        with self.lock:
            if ws in self.index_map:
                return self.index_map[ws]
            
            safe = SafeConn(ws)
            self.conn_map[safe] = True
            self.index_map[ws] = safe
            return safe
    
    def check_if_connection_exists(self, ws: websocket.WebSocket) -> bool:
        with self.lock:
            return ws in self.index_map
    
    def write_message(self, ws: websocket.WebSocket, data: bytes) -> Optional[str]:
        with self.lock:
            safe = self.index_map.get(ws)
        
        if not safe:
            return "connection not found"
        
        with safe.lock:
            try:
                safe.ws.send(data)
                return None
            except Exception as e:
                return str(e)
    
    def delete_connection(self, ws: websocket.WebSocket):
        with self.lock:
            if ws in self.index_map:
                _set_shutdown_flag(ws)
                safe = self.index_map[ws]
                del self.conn_map[safe]
                del self.index_map[ws]
                try:
                    safe.ws.close()
                except:
                    pass
                _clear_tracked_subscriptions(ws)
                return

connections = ConnectionManager()

subscription_tracker = {}

def _track_subscription(ws: websocket.WebSocket, tokens: List[str], subscription_type: str):
    ws_id = id(ws)
    if ws_id not in subscription_tracker:
        subscription_tracker[ws_id] = {
            'tokens': [],
            'option_greeks_tokens': []
        }
    
    for token in tokens:
        if token not in subscription_tracker[ws_id][subscription_type]:
            subscription_tracker[ws_id][subscription_type].append(token)

def _untrack_subscription(ws: websocket.WebSocket, tokens: List[str], subscription_type: str):
    ws_id = id(ws)
    if ws_id in subscription_tracker and subscription_type in subscription_tracker[ws_id]:
        for token in tokens:
            if token in subscription_tracker[ws_id][subscription_type]:
                subscription_tracker[ws_id][subscription_type].remove(token)

def _get_tracked_subscriptions(ws: websocket.WebSocket) -> dict:
    ws_id = id(ws)
    return subscription_tracker.get(ws_id, {'tokens': [], 'option_greeks_tokens': []})

def _clear_tracked_subscriptions(ws: websocket.WebSocket):
    ws_id = id(ws)
    if ws_id in subscription_tracker:
        del subscription_tracker[ws_id]

def get_url_and_header_data(user_id: str, config: dict) -> tuple:
    scheme = config.get('scheme', 'wss')
    host = config.get('host')
    path = config.get('path')
    src_val = config.get('source', 'API')
    accept_encoding = config.get('accept_encoding', 'gzip, deflate, br')
    accept_language = config.get('accept_language', 'en-US,en;q=0.9')
    origin = config.get('origin', '')
    
    base_url = f"{scheme}://{host}{path}"
    
    with open('config.json', 'r') as f:
        config_json = json.load(f)
    user_id = list(config_json.keys())[0]
    jkey = config_json[user_id]['jKey']
    
    query_params = {
        'userId': user_id, 
        'jKey': jkey,   
        'source': "developer-api"  
    }
    
    url_with_params = f"{base_url}?{urlencode(query_params)}"
    
    headers = {
        'accept-encoding': accept_encoding,
        'accept-language': accept_language,
        'cache-control': 'no-cache',
        'origin': origin,
        'pragma': 'no-cache'
    }
    
    return url_with_params, headers, None

def _identify_update_type(data: Dict) -> UpdateType:
    if "norenordno" in data:
        return UpdateType.ORDER
    elif "brkname" in data:
        return UpdateType.POSITION
    elif "gamma" in data: 
        return UpdateType.OPTION_GREEKS
    else:
        return UpdateType.MARKET_FEED

def _handle_authentication_response(message: str) -> bool:
    if "Authentication successful" in message:
        return True
    elif '"status":"failed"' in message:
        return False
    return True

shutdown_flags = {}

def _set_shutdown_flag(ws: websocket.WebSocket):
    ws_id = id(ws)
    shutdown_flags[ws_id] = True

def _is_shutdown_requested(ws: websocket.WebSocket) -> bool:
    ws_id = id(ws)
    return shutdown_flags.get(ws_id, False)

def _clear_shutdown_flag(ws: websocket.WebSocket):
    ws_id = id(ws)
    if ws_id in shutdown_flags:
        del shutdown_flags[ws_id]

def read_message(user_id: str, ws: websocket.WebSocket, model: dict, config: dict):
    max_retries = config.get('max_websocket_connection_retries', 3)
    time_interval = config.get('time_interval', 5)
    
    is_authenticated = True
    
    subscribed_tokens = model.get('tokens', [])
    subscribed_option_greeks_tokens = model.get('option_greeks_tokens', [])
    
    while True:
        if not connections.check_if_connection_exists(ws):
            _clear_shutdown_flag(ws)
            return
        
        try:
            message = ws.recv()
            
            if not message:
                continue
            
            try:
                data = json.loads(message)
            except json.JSONDecodeError as e:
                continue
            
            # Handle authentication responses
            if "status" in data and "message" in data:
                if _handle_authentication_response(message):
                    is_authenticated = True
                continue
            
            # Route messages to appropriate callbacks
            update_type = _identify_update_type(data)
            
            if update_type == UpdateType.ORDER:
                if model.get('order_data'):
                    try:
                        model['order_data'](data)
                    except Exception as e:
                        pass
            
            elif update_type == UpdateType.POSITION:
                if model.get('position_data'):
                    try:
                        model['position_data'](data)
                    except Exception as e:
                        pass
            
            elif update_type == UpdateType.OPTION_GREEKS:
                if model.get('subscribe_option_greeks_data'):
                    try:
                        if isinstance(data, dict):
                            for key, value in data.items():
                                if isinstance(value, dict) and "gamma" in value:
                                    model['subscribe_option_greeks_data'](value)
                    except Exception as e:
                        pass
            
            else:  # Market feed
                if model.get('subscribe_feed_data'):
                    try:
                        model['subscribe_feed_data'](data)
                    except Exception as e:
                        pass
        
        except (websocket.WebSocketConnectionClosedException, 
                websocket.WebSocketProtocolException,
                Exception) as e:
            
            # Check if shutdown was requested
            if _is_shutdown_requested(ws):
                _clear_shutdown_flag(ws)
                return
            
            if not connections.check_if_connection_exists(ws):
                return
            
            # Attempt reconnection
            new_ws = _attempt_reconnection(
                user_id, ws, config, max_retries, time_interval,
                subscribed_tokens, subscribed_option_greeks_tokens
            )
            
            if new_ws is None:
                return
            
            # Update local reference
            ws = new_ws
            is_authenticated = True
            
            # Call user's reconnection callback if provided
            if model.get('on_reconnect'):
                try:
                    model['on_reconnect'](new_ws)
                except Exception as callback_error:
                    pass
            
            continue

def _attempt_reconnection(
    user_id: str,
    old_ws: websocket.WebSocket,
    config: dict,
    max_retries: int,
    time_interval: int,
    subscribed_tokens: List[str],
    subscribed_option_greeks_tokens: List[str]
) -> Optional[websocket.WebSocket]:
    # Get the actual tracked subscriptions
    tracked = _get_tracked_subscriptions(old_ws)
    all_tokens = tracked['tokens']
    all_option_greeks_tokens = tracked['option_greeks_tokens']
    
    for attempt in range(1, max_retries + 1):
        if not connections.check_if_connection_exists(old_ws):
            return None
        
        time.sleep(time_interval)
        
        try:
            # Create new connection
            base_url, headers, err = get_url_and_header_data(user_id, config)
            if err:
                continue
            
            new_ws = websocket.create_connection(base_url, header=headers)
            
            # Wait for authentication message
            msg = new_ws.recv()
            
            if "Authentication successful" not in msg:
                new_ws.close()
                continue
            
            # Transfer subscription tracking
            old_ws_id = id(old_ws)
            new_ws_id = id(new_ws)
            
            if old_ws_id in subscription_tracker:
                subscription_tracker[new_ws_id] = subscription_tracker[old_ws_id].copy()
            
            # Update connection manager
            connections.delete_connection(old_ws)
            connections.add_connection(new_ws)
            
            # Resubscribe to market feed tokens
            if all_tokens:
                time.sleep(0.5)
                tokens_str = "|".join(all_tokens)
                msg = json.dumps({"action": "subscribe", "tokens": tokens_str})
                
                error = connections.write_message(new_ws, msg.encode())
            
            # Resubscribe to option Greeks tokens
            if all_option_greeks_tokens:
                time.sleep(0.5)
                tokens_str = "|".join(all_option_greeks_tokens)
                msg = json.dumps({"action": "subscribe-option-greeks", "tokens": tokens_str})
                
                error = connections.write_message(new_ws, msg.encode())
            
            time.sleep(1)
            
            return new_ws
        
        except Exception as e:
            if attempt == max_retries:
                return None
    
    return None

def subscribe(ws: websocket.WebSocket, tokens: List[str]) -> Optional[dict]:
    if not connections.check_if_connection_exists(ws):
        return {
            "error": {
                "message": "Connection does not exist"
            }
        }
    
    _track_subscription(ws, tokens, 'tokens')
    
    if len(tokens) == 1 and "|" in tokens[0]:
        tokens_str = tokens[0]
    else:
        tokens_str = "|".join(tokens)
    
    msg = json.dumps({
        "action": "subscribe",
        "tokens": tokens_str
    })
    
    error = connections.write_message(ws, msg.encode())
    
    if error:
        return {"error": {"message": error}}
    
    return None

def unsubscribe(ws: websocket.WebSocket, tokens: List[str]) -> Optional[dict]:
    if not connections.check_if_connection_exists(ws):
        return {
            "error": {
                "message": "Connection does not exist"
            }
        }
    
    _untrack_subscription(ws, tokens, 'tokens')
    
    tokens_str = "|".join(tokens)
    msg = json.dumps({
        "action": "unsubscribe",
        "tokens": tokens_str
    })
    
    error = connections.write_message(ws, msg.encode())
    
    if error:
        return {"error": {"message": error}}
    
    return None

def subscribe_option_greeks(ws: websocket.WebSocket, tokens: List[str]) -> Optional[dict]:
    if not connections.check_if_connection_exists(ws):
        return {
            "error": {
                "message": "Connection does not exist"
            }
        }
    
    _track_subscription(ws, tokens, 'option_greeks_tokens')
    
    if len(tokens) == 1 and "|" in tokens[0]:
        tokens_str = tokens[0]
    else:
        tokens_str = "|".join(tokens)
    
    msg = json.dumps({
        "action": "subscribe-option-greeks",
        "tokens": tokens_str
    })
    
    error = connections.write_message(ws, msg.encode())
    
    if error:
        return {"error": {"message": error}}
    
    return None

def unsubscribe_option_greeks(ws: websocket.WebSocket, tokens: List[str]) -> Optional[dict]:
    if not connections.check_if_connection_exists(ws):
        return {
            "error": {
                "message": "Connection does not exist"
            }
        }
    
    _untrack_subscription(ws, tokens, 'option_greeks_tokens')
    
    if len(tokens) == 1 and "|" in tokens[0]:
        tokens_str = tokens[0]
    else:
        tokens_str = "|".join(tokens)
    
    msg = json.dumps({
        "action": "unsubscribe-option-greeks",
        "tokens": tokens_str
    })
    
    error = connections.write_message(ws, msg.encode())
    
    if error:
        return {"error": {"message": error}}
    
    return None