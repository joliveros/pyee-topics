# -*- coding: utf-8 -*-

"""
pyee supplies an ``EventEmitter`` object similar to the ``EventEmitter``
from Node.js. It supports both synchronous callbacks and asyncio coroutines.

There is also the possibility to use mqtt topic patterns to match events

Example
-------

::

    In [1]: from pyee import EventEmitter

    In [2]: ee = EventEmitter()

    In [3]: @ee.on('event')
       ...: def event_handler():
       ...:     print('BANG BANG')
       ...:

    In [4]: ee.emit('event')
    BANG BANG

    In [5]:

    In [6]: ee.on('a/#/c', lambda ...)

Easy-peasy.


"""

try:
    from asyncio import iscoroutine, ensure_future
except ImportError:
    iscoroutine = None
    ensure_future = None

class PatternException(Exception):
    pass

from collections import defaultdict

__all__ = ['EventEmitter', 'PyeeException']


class PyeeException(Exception):
    """An exception internal to pyee."""
    pass


class EventEmitter(object):

    """The EventEmitter class.

    For interoperation with asyncio, one can specify the scheduler and
    the event loop. The scheduler defaults to ``asyncio.ensure_future``,
    and the loop defaults to ``None``. When used with the default scheduler,
    this will schedule the coroutine onto asyncio's default loop.

    This should also be compatible with recent versions of twisted by
    setting ``scheduler=twisted.internet.defer.ensureDeferred``.

    Most events are registered with EventEmitter via the ``on`` and ``once``
    methods. However, pyee EventEmitters have two *special* events:

    - ``new_listener``: Fires whenever a new listener is created. Listeners for
      this event do not fire upon their own creation.

    - ``error``: When emitted raises an Exception by default, behavior can be
      overriden by attaching callback to the event.

      For example::

          @ee.on('error')
          def onError(message):
              logging.err(message)

          ee.emit('error', Exception('something blew up'))

      For synchronous callbacks, exceptions are **not** handled for you---
      you must catch your own exceptions inside synchronous ``on`` handlers.
      However, when wrapping **async** functions, errors will be intercepted
      and emitted under the ``error`` event. **This behavior for async
      functions is inconsistent with node.js**, which unlike this package has
      no facilities for handling returned Promises from handlers.
    """
    def __init__(self, scheduler=ensure_future, loop=None):
        self._events = defaultdict(list)
        self._schedule = scheduler
        self._loop = loop

        # Specialised dict for pattern matching topics
        # This way it will not impact standard behaviour
        self._patterns = defaultdict(list)

    def on(self, event, f=None):
        """Registers the function (or optionally an asyncio coroutine function)
        ``f`` to the event name ``event``.

        If ``f`` isn't provided, this method returns a function that
        takes ``f`` as a callback; in other words, you can use this method
        as a decorator, like so::

            @ee.on('data')
            def data_handler(data):
                print(data)

        As mentioned, this method can also take an asyncio coroutine function::

           @ee.on('data')
           async def data_handler(data)
               await do_async_thing(data)


        This will automatically schedule the coroutine using the configured
        scheduling function (defaults to ``asyncio.ensure_future``) and the
        configured event loop (defaults to ``asyncio.get_event_loop()``).
        """

        def _on(f):
            # Fire 'new_listener' *before* adding the new listener!
            self.emit('new_listener', event, f)

            # Add the necessary function
            if self._isPattern(event):
                self._patterns[event].append(f)
            else:
                self._events[event].append(f)

            # Return original function so removal works
            return f

        if f is None:
            return _on
        else:
            return _on(f)

    def emit(self, event, *args, **kwargs):
        """Emit ``event``, passing ``*args`` and ``**kwargs`` to each attached
        function. Returns ``True`` if any functions are attached to ``event``;
        otherwise returns ``False``.

        Example::

            ee.emit('data', '00101001')

        Assuming ``data`` is an attached function, this will call
        ``data('data', '00101001')'``.

        For coroutine event handlers, calling emit is non-blocking. In other
        words, you do not have to await any results from emit, and the
        coroutine is scheduled in a fire-and-forget fashion.
        """
        handled = False

        patterns_copy = list(self._patterns)
        for p in patterns_copy:
            if self._matches(p, event):
                for f in self._patterns[p]:
                    result = f(event, *args, **kwargs)
                    if iscoroutine and iscoroutine(result):
                        self.handle_coroutine(result)

        # Copy the events dict first. Avoids a bug if the events dict gets
        # changed in the middle of the following for loop.
        events_copy = list(self._events[event])

        # Pass the args to each function in the events dict
        for f in events_copy:
            result = f(*args, **kwargs)
            if iscoroutine and iscoroutine(result):
                self.handle_coroutine(result)

            handled = True

        if not handled and event == 'error':
            if len(args):
                raise args[0]
            else:
                raise PyeeException("Uncaught, unspecified 'error' event.")

        return handled

    def handle_coroutine(self, result):
        if self._loop:
                d = self._schedule(result, loop=self._loop)
        else:
            d = self._schedule(result)
        if hasattr(d, 'add_done_callback'):
            @d.add_done_callback
            def _callback(f):
                exc = f.exception()
                if exc:
                    self.emit('error', exc)
        elif hasattr(d, 'addErrback'):
            @d.addErrback
            def _callback(exc):
                self.emit('error', exc)

    def _isPattern(self, pattern):
        """is there any /+/ or /#/ in the pattern?"""
        if '#' in pattern and not pattern.endswith('#'):
            return False
        return any(filter(lambda x: x == '+' or x == '#', pattern.split('/')))

    def _matches(self, pattern, event):
        "Check that 'a/+/b/+/c' pattern matches '/a/x/b/x/c'"

        if '#' in pattern and not pattern.endswith('#'):
            raise PatternException

        ps, es = pattern.split('/'), event.split('/')
        return all([x == y or x == '+' or (x == '#' and len(ps) <= len(es)) for x, y in zip(ps, es)]) and len(ps) <= len(es)

    def once(self, event, f=None):
        """The same as ``ee.on``, except that the listener is automatically
        removed after being called.
        """
        def _once(f):
            def g(*args, **kwargs):
                f(*args, **kwargs)
                self.remove_listener(event, g)
            return g

        def _wrapper(f):
            self.on(event, _once(f))
            return f

        if f is None:
            return _wrapper
        else:
            _wrapper(f)

    def remove_listener(self, event, f):
        """Removes the function ``f`` from ``event``."""
        if self._isPattern(event):
            self._patterns[event].remove(f)
        else:
            self._events[event].remove(f)

    def remove_all_listeners(self, event=None):
        """Remove all listeners attached to ``event``.
        If ``event`` is ``None``, remove all listeners on all events.
        """
        if event is not None:
            if '#' in event:
                self._patterns[event] = []
            else:
                self._events[event] = []
        else:
            self._events = None
            self._patterns = None
            self._events = defaultdict(list)
            self._patterns = defaultdict(list)

    def listeners(self, event):
        """Returns the list of all listeners registered to the ``event``.
        """
        return self._events[event] if not self._isPattern(event) else self._patterns[event]

# Backwards compatiblity
Event_emitter = EventEmitter
