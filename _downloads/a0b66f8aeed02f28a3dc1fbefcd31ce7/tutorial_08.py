import asyncio
import hat.stc

door_states = hat.stc.parse_scxml('door_05.scxml')

class Door:

    def __init__(self, max_counter):
        actions = {'logEnter': self._act_log_enter,
                   'logExit': self._act_log_exit,
                   'logTransition': self._act_log_transition,
                   'logInvalid': self._act_log_invalid,
                   'startTimer': self._act_start_timer,
                   'stopTimer': self._act_stop_timer,
                   'incCounter': self._act_inc_counter}
        conditions = {'isOperational': self._cond_is_operational}
        self._max_counter = max_counter
        self._counter = 0
        self._timer = None
        self._stc = hat.stc.Statechart(door_states, actions, conditions)
        self._runner = hat.stc.AsyncRunner()

    async def finish(self):
        await self._runner.async_close()

    def close(self, force):
        print('registering close event')
        self._runner.register(self._stc, hat.stc.Event('close', force))

    def open(self, force):
        print('registering open event')
        self._runner.register(self._stc, hat.stc.Event('open', force))

    def _act_log_enter(self, stc, evt):
        print(f'entering state {stc.state}')

    def _act_log_exit(self, stc, evt):
        print(f'exiting state {stc.state}')

    def _act_log_transition(self, stc, evt):
        print(f'transitioning because of event {evt}')

    def _act_log_invalid(self, stc, evt):
        print(f'invalid operation {evt.name} in state {stc.state}')

    def _act_start_timer(self, stc, evt):
        force = evt.payload
        delay = force_to_delay(force)
        print(f'waiting for {delay} seconds')
        loop = asyncio.get_event_loop()
        self._timer = loop.call_later(delay, self._runner.register, self._stc,
                                      hat.stc.Event('timeout'))

    def _act_stop_timer(self, stc, evt):
        self._timer.cancel()

    def _act_inc_counter(self, stc, evt):
        self._counter += 1

    def _cond_is_operational(self, stc, evt):
        return self._counter < self._max_counter

def force_to_delay(force):
    if force <= 0:
        return 0.1
    if force >= 100:
        return 0
    return (100 - force) * 0.001

async def main():
    door = Door(3)
    await asyncio.sleep(1)

    door.close(10)
    await asyncio.sleep(1)

    door.open(20)
    await asyncio.sleep(1)

    door.close(30)
    await asyncio.sleep(1)

    # we already operated on this door instance 3 times
    door.open(40)
    await asyncio.sleep(1)

    await door.finish()

if __name__ == '__main__':
    asyncio.run(main())
