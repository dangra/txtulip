"""
Tests for txtulip.eventloop.
"""

from unittest import TestCase

from twisted.test.proto_helpers import MemoryReactor

from ..eventloop import (
    TwistedEventLoop, _noop, _GenericFileDescriptor, _Callable,
    )


class FileDescriptorRegistrationTests(TestCase):
    """
    Tests for the add/remove_reader/writer API.
    """
    def setUp(self):
        self.reactor = MemoryReactor()
        self.eventloop = TwistedEventLoop(self.reactor)

    def assert_descriptor_has_callbacks(self, fd, read_callback,
                                        write_callback):
        fd_wrappers = set(
            [wrapper for wrapper in
             self.reactor.getReaders() + self.reactor.getWriters()
             if wrapper.fileno() == fd])
        self.assertEqual(len(fd_wrappers), 1)
        wrapper = fd_wrappers.pop()
        self.assertEqual((wrapper.__class__, wrapper.fileno(),
                          wrapper._readCallback, wrapper._writeCallback),
                         (_GenericFileDescriptor, fd, read_callback,
                          write_callback))

    def test_add_reader_callback(self):
        """
        For a new fd, the callback passed to add_reader is hooked up to the
        Twisted FileDescriptor's doRead, and a no-op for doWrite.
        """
        func = lambda: None
        self.eventloop.add_reader(123, func, 1, 2)
        self.eventloop.add_reader(125, func, 1)
        self.assert_descriptor_has_callbacks(123, _Callable(func, (1, 2)),
                                             _noop)
        self.assert_descriptor_has_callbacks(125, _Callable(func, (1,)),
                                             _noop)

    def test_add_writer_callback(self):
        """
        For a new fd, the callback passed to add_writer is hooked up to the
        Twisted FileDescriptor's doWrite, and a no-op for doRead.
        """
        func = lambda: None
        self.eventloop.add_writer(123, func, 1, 2)
        self.eventloop.add_writer(125, func, 5)
        self.assert_descriptor_has_callbacks(123, _noop, _Callable(func, (1, 2)))
        self.assert_descriptor_has_callbacks(125, _noop, _Callable(func, (5,)))

    def test_remove_reader_callback(self):
        """
        For a new fd that is only added with add_reader, the FileDescriptor for
        the fd removed by remove_reader.
        """
        self.eventloop.add_reader(123, lambda: None, 1, 2)
        self.eventloop.add_reader(124, lambda: None)
        self.eventloop.remove_reader(123)
        self.assertEqual([f.fileno() for f in self.reactor.getReaders()], [124])

    def test_remove_writer_callback(self):
        """
        For a new fd that is only added with add_writer, the FileDescriptor for
        the fd removed by remove_writer.
        """
        self.eventloop.add_writer(123, lambda: None, 1, 2)
        self.eventloop.add_writer(124, lambda: None)
        self.eventloop.remove_writer(123)
        self.assertEqual([f.fileno() for f in self.reactor.getWriters()], [124])

    def test_remove_reader_twice(self):
        """
        Calling remove_reader a second time has no effect.
        """
        self.eventloop.add_reader(123, lambda: None, 1, 2)
        self.eventloop.remove_reader(123)
        self.eventloop.remove_reader(123)

    def test_remove_writer_twice(self):
        """
        Calling remove_writer a second time has no effect.
        """
        self.eventloop.add_writer(123, lambda: None, 1, 2)
        self.eventloop.remove_writer(123)
        self.eventloop.remove_writer(123)

    def test_add_reader_twice(self):
        """
        Calling add_reader a second time overrides the first callback.
        """

    def test_add_writer_twice(self):
        """
        Calling add_writer a second time overrides the first callback.
        """

    def test_add_reader_add_writer(self):
        """
        If a new fd is added with add_reader and then add_writer, both callbacks
        are hooked up to a Twisted FileDescriptor.
        """

    def test_add_writer_add_reader(self):
        """
        If a new fd is added with add_writer and then add_reader, both callbacks
        are hooked up to a Twisted FileDescriptor.
        """

    def test_remove_both(self):
        """
        If a new fd is added as both reader and writer, the FileDescriptor for
        the fd is removed if both remove_writer and remove_reader are called.
        """

    def test_add_both_remove_reader(self):
        """
        If a new fd is added as both reader and writer, the FileDescriptor for
        the fd is not removed if only remove_writer is called.
        """

    def test_add_both_remove_writer(self):
        """
        If a new fd is added as both reader and writer, the FileDescriptor for
        the fd is not removed if only remove_reader is called.
        """
