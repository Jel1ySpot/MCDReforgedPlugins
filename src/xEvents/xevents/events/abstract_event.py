import re
import typing

import mcdreforged.api.types as types
import mcdreforged.plugin.plugin_event as event

class AbstractEvent:
    def __init__(self, server: types.PluginServerInterface) -> None:
        self.event_id = ''
        self.server = server

    def dispatch(self, *args) -> None:
        self.server.dispatch_event(event.LiteralEvent(self.event_id), args)