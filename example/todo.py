# this not finish yet
from dataclasses import dataclass
import datetime

import keyboard

from fsm import FSM
from src.board_support import keyboad_support
import sys


class Corlor:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    END = "\033[0m"


def hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()


def recover_cursor():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()


@dataclass
class TodoItem:
    state: bool
    title: str
    content: str
    time: str


@keyboad_support
class EditPannle(FSM):
    def __init__(self) -> None:
        super().__init__()
        self.bind_board({ # type: ignore
            "rigth":"move",
            "left": "move",
            "enter": "save"
        })

    def init(self):
        return

    def halt(self):
        return super().halt()

    def show_detail(self):
        cur_todo = self.ctx.todos[self.ctx.cur_index]
        print(dict(cur_todo))
        self.wait("enter")
    def edit_line(self):
        self.ctx.cur_index



@keyboad_support
class TODO(FSM):
    def __init__(self) -> None:
        super().__init__()
        self.ctx.todos = [
            TodoItem(False, "todo 1", "todo...", "1"),
            TodoItem(False, "todo 2", "todo...", "2"),
        ]
        self.ctx.cur_index = 0
        hide_cursor()
        self.bind_board({"up": "move", "down": "move", "enter": "check"}) # type: ignore

    def init(self):
        self.to(self.show)

    def halt(self):
        return super().halt()

    def show(self):
        for i, line in enumerate(self.ctx.todos):
            if i == self.ctx.cur_index:
                print(Corlor.GREEN + str(line) + Corlor.END)
            else:
                print(line)
        self.to(self.operate)

    def delete_previous_lines(self):
        for _ in range(len(self.ctx.todos)):
            print("\033[A", end="")
            print("\033[K", end="")
        print("", end="", flush=True)
        self.to(self.show)

    def operate(self):
        with self.listen("check", "new", "delete", "edit", "move") as e:
            match e.event:
                case "move":
                    self.ctx.cur_index -= (
                        1 if self.ctx.cur_index > 0 and e.kwargs["key"] == "up" else 0
                    )
                    self.ctx.cur_index += (
                        1
                        if self.ctx.cur_index < len(self.ctx.todos) - 1
                        and e.kwargs["key"] == "down"
                        else 0
                    )
                    self.to(self.delete_previous_lines)
                case "check":
                    self.ctx.todos[self.ctx.cur_index].state = not self.ctx.todos[
                        self.ctx.cur_index
                    ].state
                    self.to(self.delete_previous_lines)
                case "new":
                    cur_time = self._get_cur_time()
                    self.ctx.todos.insert(0, TodoItem(False, "", "", cur_time))
                    self.ctx.cur_index = 0
                    self.call_sub(EditPannle, self.delete_previous_lines)
                case "edit":
                    self.call_sub(EditPannle, self.delete_previous_lines)
                case "delete":
                    self.ctx.todos.pop(self.ctx.cur_index)
                    self.to(self.delete_previous_lines)

    def _get_cur_time(self):
        return datetime.datetime.now().strftime("%m-%d %H:%M:%S")


if __name__ == "__main__":
    m = TODO()
    m.run()
    keyboard.wait("esc")