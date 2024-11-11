import asyncio
import collections
import itertools
import logging

from hat import aio

from hat.stc.common import EventName, Event
from hat.stc.statechart import Action, Condition, Statechart


mlog = logging.getLogger(__name__)


class SyncRunner:

    def __init__(self):
        self._queue = collections.deque()

    @property
    def empty(self) -> bool:
        """Is event queue empty"""
        return not self._queue

    def register(self, stc: Statechart, event: Event):
        """Add event to queue"""
        self._queue.append((stc, event))

    def step(self):
        """Process next queued event"""
        if not self._queue:
            return

        stc, event = self._queue.popleft()
        stc.step(event)


class AsyncRunner(aio.Resource):

    def __init__(self):
        self._queue = aio.Queue()
        self._async_group = aio.Group()

        self.async_group.spawn(self._runner_loop)

    @property
    def async_group(self):
        """Async group"""
        return self._async_group

    def register(self, stc: Statechart, event: Event):
        """Add event to queue"""
        self._queue.put_nowait((stc, event))

    async def _runner_loop(self):
        try:
            while True:
                stc, event = await self._queue.get()
                stc.step(event)

        except Exception as e:
            mlog.error("runner loop error: %s", e, exc_info=e)

        finally:
            self.close()
            self._queue.close()


class AsyncTimer(aio.Resource):

    def __init__(self,
                 runner: AsyncRunner,
                 event: EventName,
                 duration: float):
        self._runner = runner
        self._event = event
        self._duration = duration
        self._loop = asyncio.get_running_loop()
        self._async_group = runner.async_group.create_subgroup()
        self._next_tokens = itertools.count(1)
        self._active_token = None
        self._timer = None

        self.async_group.spawn(aio.call_on_cancel, self._stop, None, None)

    @property
    def async_group(self) -> aio.Group:
        return self._async_group

    @property
    def start(self) -> Action:
        return self._start

    @property
    def stop(self) -> Action:
        return self._stop

    @property
    def condition(self) -> Condition:
        return self._condition

    def _start(self, stc, _):
        if not self.is_open:
            return

        if self._timer:
            self._timer.cancel()

        self._active_token = next(self._next_tokens)
        self._timer = self._loop.call_later(self._duration, self._on_timer,
                                            stc, self._active_token)

    def _stop(self, _, __):
        self._active_token = None
        if not self._timer:
            return

        self._timer.cancel()
        self._timer = None

    def _condition(self, _, event):
        return bool(event and event.payload == self._active_token)

    def _on_timer(self, stc, token):
        if not self.is_open:
            return

        self._runner.register(stc, Event(name=self._event,
                                         payload=token))
