import keyboard
import time
from typing import Any, Callable, Dict, override
from fsm import FSM

def keyboad_support(cls):
    class KeyBoardFSM(cls):
        def bind_board(
            self, key_to_event: Dict[str, str] = {}, debounce_time: float = 0.1
        ):
            self.key_to_event = key_to_event
            keyboard.unhook_all()
            last_press_time: Dict[str, float] = {}

            def on_key_event(event: keyboard.KeyboardEvent):
                if event.event_type != keyboard.KEY_DOWN:
                    return

                key_name = event.name
                if key_name is None:
                    return

                if key_name == "esc":
                    keyboard.unhook_all()
                    return

                current_time = time.time()
                last_time = last_press_time.get(key_name, 0)
                if current_time - last_time < debounce_time:
                    return

                last_press_time[key_name] = current_time
                event_name = key_to_event.get(key_name)
                if event_name is None:
                    return
                self.send(event_name, key=key_name)

            for k in key_to_event.keys():
                keyboard.hook_key(k, on_key_event, True)

        @override
        def call_sub(self, subfsm_cls: Callable[..., FSM], state: Callable[..., Any]): # type: ignore
            super().call_sub(subfsm_cls, state)
            self.bind_board(self.key_to_event)
    return KeyBoardFSM
