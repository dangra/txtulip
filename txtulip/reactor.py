"""
Reactor implementation.
"""

from asyncio import get_event_loop, new_event_loop

from twisted.internet.base import DelayedCall
from twisted.internet.posixbase import PosixReactorBase
from twisted.python.log import callWithLogger


class AsyncioSelectorReactor(PosixReactorBase):
    """
    Reactor running on top of an asyncio SelectorEventLoop.
    """
    _asyncClosed = False

    def __init__(self, eventloop):
        self._asyncioEventloop = eventloop
        PosixReactorBase.__init__(self)


    def _doReadOrWrite(self, selectable, read):
        method = selectable.doRead if read else selectable.doWrite
        try:
            why = method()
        except Exception as e:
            why = e
        if why:
            self._disconnectSelectable(selectable, why, read)


    def addReader(self, reader):
        fd = reader.fileno()
        self._asyncioEventloop.add_reader(fd, callWithLogger, reader,
                                          self._doReadOrWrite, reader, True)


    def addWriter(self, writer):
        fd = writer.fileno()
        self._asyncioEventloop.add_writer(fd, callWithLogger, writer,
                                          self._doReadOrWrite, writer, False)


    def removeReader(self, reader):
        fd = reader.fileno()
        self._asyncioEventloop.remove_reader(fd)


    def removeWriter(self, writer):
        fd = writer.fileno()
        self._asyncioEventloop.remove_writer(fd)


    def removeAll(self):
        return []


    def doIteration(self, timeout):
        self._asyncioEventloop.call_later(timeout, self._asyncioEventloop.stop)
        self._asyncioEventloop.run_forever()


    def run(self):
        self._asyncioEventloop.run_forever()

    def stop(self):
        self._asyncioEventloop.stop()

    def crash(self):
        self._asyncioEventloop.stop()


    def seconds(self):
        return self._asyncioEventloop.time()


    def callLater(self, seconds, f, *args, **kwargs):
        handle = self._asyncioEventloop.call_later(seconds, f, *args, **kwargs)
        def reset(dc):
            print("NOT IMPLEMENTED YET")

        dc = DelayedCall(self.seconds() + seconds, f, args, kwargs,
                         lambda dc: handle.cancel(), reset,
                         seconds=self.seconds)
        self._newTimedCalls.append(dc)
        return dc



@staticmethod
def _reactorForTesting():
    return AsyncioSelectorReactor(new_event_loop())
def _installTestInfrastructure():
    from twisted.internet.test.reactormixins import ReactorBuilder
    ReactorBuilder._reactors.append("txtulip.reactor._reactorForTesting")
_installTestInfrastructure()



def install(eventloop=None):
    if eventloop is None:
        eventloop = get_event_loop()
    reactor = AsyncioSelectorReactor(eventloop)
    from twisted.internet.main import installReactor
    installReactor(reactor)

