## SimpleFSM

It's a simple fsm implement for Finity State Machine.

This fsm can be embedded in your scripts as an easier substitution of heavy frameworks (e.g xstate).

Using this small tool can make your code (especially interactive code) clearer.

## Usage

```python
from time import sleep
from fsm import FSM 

class MyMachine(FSM):
    def __init__(self):
        super().__init__()

    # you must rewrite init and halt method.
    # these two are important states for your fsm.
    def init(self):
        self.to(self.state1)

    def halt(self):
        return super().halt()

    def state1(self):
        self.to(self.state2)
    

    def state2(self):
        delta = self.wait("new-int-come")
        name, age = self.wait("new-info-come") # you can also disable quick unpack to receive a dict
        age += delta
        print(f"{name} age: {age}")
        self.to(self.halt)
    
machine = MyMachine()
machine.run()
machine.send("new-int-come", i=10)
machine.send("new-info-come", name="lith", age=10)
sleep(1)
```
