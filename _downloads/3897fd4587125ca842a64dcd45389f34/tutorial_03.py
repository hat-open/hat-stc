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

    def close(self):
        print('registering close event')
        self._runner.register(self._stc, hat.stc.Event('close'))

    def open(self):
        print('registering open event')
        self._runner.register(self._stc, hat.stc.Event('open'))

    def _act_print_state(self, stc, evt):
        print('current state:', stc.state)

def main():
    door = Door()
    door.run()

    door.close()
    door.run()

    door.open()
    door.run()

if __name__ == '__main__':
    main()
