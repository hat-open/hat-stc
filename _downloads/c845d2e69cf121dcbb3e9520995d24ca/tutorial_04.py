import hat.stc

door_states = hat.stc.parse_scxml('door_01.scxml')

class Door:

    def __init__(self):
        actions = {'printState': self._act_print_state}
        self._stc = hat.stc.Statechart(door_states, actions)
        self._runner = hat.stc.SyncRunner()

    def run(self):
        while not self._runner.empty:
            self._runner.step()

    def close(self, force):
        print('registering close event')
        self._runner.register(self._stc, hat.stc.Event('close', force))

    def open(self, force):
        print('registering open event')
        self._runner.register(self._stc, hat.stc.Event('open', force))

    def _act_print_state(self, stc, evt):
        force = evt.payload if evt else None
        print(f'force {force} caused transition to {stc.state}')

def main():
    print("1. example:")
    door = Door()
    door.run()

    door.close(10)
    door.run()

    door.open(20)
    door.run()
    print('---')

    print("2. example:")
    door = Door()
    door.close(20)
    door.open(50)

    door.run()
    print('---')

    print("3. example:")
    door = Door()
    door.open(10)
    door.close(20)
    door.close(30)
    door.open(40)

    door.run()
    print('---')

if __name__ == '__main__':
    main()
