from functools import wraps

class WebSocketManager:
    def __init__(self):
        self.subscriptions = set()

    def check_subscription(self, topic):
        return topic in self.subscriptions

    def add_subscription(self, topic):
        self.subscriptions.add(topic)

    def remove_subscription(self, topic):
        self.subscriptions.discard(topic)

ws_manager = WebSocketManager()

def websocket_subscription(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        topic = f"orderbook.50.{kwargs.get('symbol')}"
        if not ws_manager.check_subscription(topic):
            ws_manager.add_subscription(topic)
            return func(*args, **kwargs)
        else:
            print(f"Already subscribed to {topic}")
    return wrapper
