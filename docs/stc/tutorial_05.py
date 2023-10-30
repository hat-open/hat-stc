import asyncio
import hat.stc

door_states = hat.stc.parse_scxml('door_02.scxml')

class Door:

    def __init__(self):
        actions = {'logEnter': self._act_log_enter,
                   'logExit': self._act_log_exit,
                   'logTransition': self._act_log_transition,
                   'startTimer': self._act_start_timer}
        self._stc = hat.stc.Statechart(door_states, actions)
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

    def _act_start_timer(self, stc, evt):
        force = evt.payload
        delay = force_to_delay(force)
        print(f'waiting for {delay} seconds')
        loop = asyncio.get_event_loop()
        loop.call_later(delay, self._runner.register, self._stc,
                        hat.stc.Event('timeout'))

def force_to_delay(force):
    if force <= 0:
        return 0.1
    if force >= 100:
        return 0
    return (100 - force) * 0.001

async def main():
    door = Door()
    await asyncio.sleep(1)

    door.close(30)
    await asyncio.sleep(1)

    door.open(60)
    await asyncio.sleep(1)

    await door.finish()

if __name__ == '__main__':
    asyncio.run(main())
