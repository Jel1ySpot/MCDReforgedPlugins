import re

from mcdreforged.api.types import PluginServerInterface, Info
from mcdreforged.api.decorator import new_thread
from mcdreforged.plugin.plugin_event import MCDRPluginEvents

from . import abstract_event


class GetAdvancement(abstract_event.AbstractEvent):
    def parse(self, info: Info):
        # Steve has made the advancement [Stone Age]
        # Steve has completed the challenge [Uneasy Alliance]
        # Steve has reached the goal [Sky's the Limit]
        if info.is_user:
            return None
        for action in ['made the advancement', 'completed the challenge', 'reached the goal']:
            match = re.fullmatch(r'\w{1,16} has %s \[.+\]' % action, info.content)
            if match is not None:
                player, rest = info.content.split(' ', 1)
                adv = re.search(r'(?<=%s \[).+(?=\])' % action, rest).group()
                return player, adv
        return None


    @new_thread('xEvents OnPlayerMadeAdvancement')
    def on_info(self, server: PluginServerInterface, info: Info):
        result = self.parse(info)
        if result is not None:
            server.logger.debug('Player made advancement detected')
            player, advancement = result
            self.dispatch(player, advancement)
    

    def __init__(self, server: PluginServerInterface) -> None:
        super().__init__(server)
        self.event_id = 'xevents.get_advancement'

        server.register_event_listener(MCDRPluginEvents.GENERAL_INFO, self.on_info)