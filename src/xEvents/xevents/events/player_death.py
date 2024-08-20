import re
import os.path as path

from mcdreforged.api.types import PluginServerInterface, Info
from mcdreforged.api.decorator import new_thread
from mcdreforged.plugin.plugin_event import MCDRPluginEvents

from . import abstract_event, death_message

class PlayerDeath(abstract_event.AbstractEvent):
    def parse(self, info: Info) -> bool:
        if info.is_user:
            return False
        re_list = self.get_death_message_list()
        for re_exp in re_list:
            if re.fullmatch(re_exp, info.content):
                return True
        return False

    @new_thread('xEvents OnDeathMessage')
    def on_info(self, server: PluginServerInterface, info: Info) -> None:
        if self.parse(info):
            self.dispatch(info)
        
    def get_death_message_list(self):
        return death_message.RE_LIST


    def __init__(self, server: PluginServerInterface) -> None:
        super().__init__(server)
        self.event_id = 'xevents.player_death'

        server.register_event_listener(MCDRPluginEvents.GENERAL_INFO, self.on_info)