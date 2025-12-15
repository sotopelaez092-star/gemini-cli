"""事件总线"""
from typing import Callable, Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Event:
    name: str
    data: dict
    timestamp: datetime

class EventBus:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.listeners: Dict[str, List[Callable]] = {}
        return cls._instance

    def subscribe(self, event_name: str, callback: Callable):
        """订阅事件"""
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(callback)

    def publish(self, event_name: str, data: dict):
        """发布事件"""
        event = Event(name=event_name, data=data, timestamp=datetime.now())
        if event_name in self.listeners:
            for callback in self.listeners[event_name]:
                callback(event)

    def reset(self):
        """重置事件总线"""
        self.listeners = {}
