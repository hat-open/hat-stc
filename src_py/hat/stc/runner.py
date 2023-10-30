import collections
import logging

from hat import aio

from hat.stc.common import Event
from hat.stc.statechart import Statechart


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
