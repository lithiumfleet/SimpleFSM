from abc import ABC, abstractmethod
from dataclasses import dataclass
from queue import Queue
import threading
from typing import Any, Callable, Dict


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
        self.__to_thread: Queue[EventMsg]= Queue()

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
        
    def wait(self, event: Event, *, enable_quick_unpack:bool=True)-> Any:
        msg = self.__to_thread.get()
        while msg.event != event:
            msg = self.__to_thread.get()
        if enable_quick_unpack: # quick unpack
            values =tuple(msg.kwargs.values()) 
            if len(values) == 1:
                return values[0]
            else:
                return values
        return msg.kwargs
    
    def send(self, event: Event, **kwargs: Any):
        self.__to_thread.put(EventMsg(event, kwargs))

