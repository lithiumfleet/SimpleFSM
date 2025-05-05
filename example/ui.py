import random
from fsm import FSM


class NewGame(FSM):
    def __init__(self) -> None:
        super().__init__()

    def init(self):
        self.to(self.new_game)
    
    def halt(self):
        return
    
    def new_game(self):
        self.rand_num = random.randint(1, 25)
        print("game start!")
        self.to(self.guess)

    def guess(self):
        self.num = self.wait("number")
        self.to(self.check)

    def check(self):
        if self.num > self.rand_num:
            print("bigger!")
            self.to(self.guess)
        elif self.num < self.rand_num:
            print("smaller!")
            self.to(self.guess)
        else:
            print(f"correct! it's {self.rand_num}")
            self.to(self.halt)


class UI(FSM):
    def __init__(self) -> None:
        super().__init__()

    def init(self):
        print("press enter to pannel")
        self.wait("enter")
        self.to(self.pannel)

    def pannel(self):
        print("welcome to pannel")
        print("this is a guess num(1,25) game:")
        self.call_sub(NewGame, self.ask_again)

    def ask_again(self):
        print("try again?(y/n)")
        self.choice = self.wait("yn")
        if self.choice:
            self.call_sub(NewGame, self.ask_again)
        else:
            self.to(self.halt)

    def halt(self):
        print("see u next time")


def main():
    ui = UI()
    t = ui.run()
    while t.is_alive():
        cmd = input()
        if cmd == "":
            ui.send("enter")
        elif cmd.strip().isdigit():
            ui.send("number", num=int(cmd.strip()))
        elif cmd.startswith(("y", "n")):
            if cmd.startswith("y"):
                ui.send("yn", choice=True)
            else:
                ui.send("yn", choice=False)
        else:
            ui.send("input", cmd=cmd)


if __name__ == "__main__":
    main()
