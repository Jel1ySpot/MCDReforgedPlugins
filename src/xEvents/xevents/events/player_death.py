import re
import os.path as path

from mcdreforged.api.types import PluginServerInterface, Info
from mcdreforged.api.decorator import new_thread
from mcdreforged.plugin.plugin_event import MCDRPluginEvents

from . import abstract_event

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
        
    def load_death_message_data(self):
        try:
            with open(path.join(path.dirname(__file__), '../resources/death_message'), 'r', encoding='utf8') as file:
                self.death_message_data = [line.strip() for line in file.readlines()]
        except:
            self.server.logger.exception('parser_manager.load_re_death_message.fail')
            self.death_message_data = []
    
    def get_death_message_list(self):
        if self.death_message_data is None:
            self.load_death_message_data()
        return self.death_message_data


    def __init__(self, server: PluginServerInterface) -> None:
        super().__init__(server)
        self.event_id = 'xevents.player_death'
        self.death_message_data = None

        server.register_event_listener(MCDRPluginEvents.GENERAL_INFO, self.on_info)