'''
Bridge EventBus callbacks to Qt signals, thread-safe.
'''

from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from core.event import Event
from core.events import Events


class EventBridge(QObject):
    """Bridge EventBus to Qt event loop."""
    sentence_received = Signal(object)
    status_changed = Signal(str, str)

    def __init__(self, event_bus, parent=None):
        super().__init__(parent)
        self._bus = event_bus
        self._bus.subscribe(Events.SENTENCE, self._on_sentence)
        self._bus.subscribe(Events.START, self._on_start)
        self._bus.subscribe(Events.STOP, self._on_stop)

    def _on_sentence(self, event: Event) -> None:
        if event.data is not None:
            self.sentence_received.emit(event.data)

    def _on_start(self, event: Event) -> None:
        self.status_changed.emit("recording", "true")

    def _on_stop(self, event: Event) -> None:
        self.status_changed.emit("recording", "false")
