from typing import Callable, Dict, List


class EventEmitter:
    def __init__(self):
        self._events: Dict[str, List[Callable]] = {}

    def on(self, event: str, callback: Callable):
        if event not in self._events:
            self._events[event] = []
        self._events[event].append(callback)

    def emit(self, event: str, *args, **kwargs):
        if event in self._events:
            for callback in self._events[event]:
                callback(*args, **kwargs)
