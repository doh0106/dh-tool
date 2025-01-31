import threading
from typing import List, Dict, Any, Callable


class EventBus:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}

    @property
    def listeners(self):
        return self._listeners

    def register(self, event: str, listener: Callable):
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(listener)

    def unregister(self, event: str, listener: Callable):
        if event in self._listeners:
            self._listeners[event].remove(listener)

    def emit(self, event: str, *args, **kwargs):
        if event in self._listeners:
            for listener in self._listeners[event]:
                listener(*args, **kwargs)
