# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.


class Observable(object):
    def __init__(self):
        object.__init__(self)

        self._event_handlers = []

    def add_listener(self, listener):
        self._event_handlers.append(listener)

    def remove_listener(self, listener):
        self._event_handlers.remove(listener)

    def clear_all(self):
        self._event_handlers = []

    def _notify(self, *args):
        for event_handler in self._event_handlers:
            event_handler(*args)
