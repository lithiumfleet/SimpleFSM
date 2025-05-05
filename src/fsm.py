from abc import ABC, abstractmethod
from dataclasses import dataclass
from queue import Queue
import threading
from typing import Any, Callable, Dict


class Context:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __getitem__(self, key):
        return self.__dict__.get(key)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getattr__(self, name):
        try:
            return self.__dict__[name]
        except KeyError:
            return None

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def __delitem__(self, key):
        del self.__dict__[key]

    def __delattr__(self, name):
        try:
            del self.__dict__[name]
        except KeyError as e:
            raise AttributeError(str(e))

    def __contains__(self, key):
        return key in self.__dict__

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __repr__(self):
        return f"Context({self.__dict__})"

    def get(self, key, default=None):
        return self.__dict__.get(key, default)

    def items(self):
        return self.__dict__.items()

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def update(self, other=None, **kwargs):
        if other is not None:
            self.__dict__.update(other)
        self.__dict__.update(kwargs)

    def to_dict(self):
        return self.__dict__.copy()


type State = Callable
type Event = str
type RespMsg = Any


@dataclass
class EventMsg:
    event: Event
    kwargs: Dict[str, Any]


class FSM(ABC):

    def __init__(self) -> None:
        super().__init__()
        self.__state: State = self.init
        self.__to_thread: Queue[EventMsg] = Queue()
        self.ctx = Context()

    @abstractmethod
    def init(self):
        self.to(self.halt)

    @abstractmethod
    def halt(self):
        exit(0)

    def to(self, state: State):
        self.__state = state

    def run(self):
        def _main():
            while self.__state != self.halt:
                self.__state()
            else:
                self.halt()

        threading.Thread(target=_main, daemon=True).start()

    def wait(self, event: Event, *, enable_quick_unpack: bool = True) -> Any:
        msg = self.__to_thread.get()
        while msg.event != event:
            msg = self.__to_thread.get()
        if enable_quick_unpack:  # quick unpack
            values = tuple(msg.kwargs.values())
            if len(values) == 1:
                return values[0]
            else:
                return values
        return msg.kwargs

    def send(self, event: Event, **kwargs: Any):
        self.__to_thread.put(EventMsg(event, kwargs))
