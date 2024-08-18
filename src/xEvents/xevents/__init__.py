from mcdreforged.api.types import PluginServerInterface
from mcdreforged.api.decorator import new_thread

from .events.player_death import PlayerDeath
from .events.get_advancement import GetAdvancement


def on_load(server: PluginServerInterface, _):
    PlayerDeath(server)
    GetAdvancement(server)