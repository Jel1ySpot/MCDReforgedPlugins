# -*- coding: utf-8 -*-
from typing import Optional, Any
import time

from mcdreforged.api import rtext
from mcdreforged.api.types import PluginServerInterface, PlayerCommandSource, Info
from mcdreforged.api.command import *
from mcdreforged.api.decorator import new_thread
from mcdreforged.plugin.plugin_event import LiteralEvent

DIMENSIONS = {
    "0": "minecraft:overworld",
    "-1": "minecraft:the_nether",
    "1": "minecraft:the_end",
    "overworld": "minecraft:overworld",
    "the_nether": "minecraft:the_nether",
    "the_end": "minecraft:the_end",
    "nether": "minecraft:the_nether",
    "end": "minecraft:the_end",
    "minecraft:overworld": "minecraft:overworld",
    "minecraft:the_nether": "minecraft:the_nether",
    "minecraft:the_end": "minecraft:the_end",
}


HELP_MESSAGE = """§6!!getback/!!b §7返回死亡地點"""



minecraft_data_api: Optional[Any]

has_command_register: bool

data: dict


def on_load(server: PluginServerInterface, _):
    global minecraft_data_api, has_command_register, data
    minecraft_data_api = server.get_plugin_instance("minecraft_data_api")

    server.register_translation(
        "zh_cn",
        {
            "help": "使用 !!getback 或 !b 回到死亡點 [§e{}§r]",
            "error": "§4找不到記錄",
            "wait": "將在三秒后傳送，請不要移動",
        },
    )
    server.register_translation(
        "en_us",
        {
            "help": "Send !!getback or !b to get back to the death pot [§e{}§r]",
            "error": "§4Could not find record",
            "wait": "Transport will take place in 3 seconds, please do not move",
        },
    )

    @new_thread("G15T getback")
    def getback(src: PlayerCommandSource, ctx):
        player = src.player
        if player not in data.keys():
            server.tell(src.player, server.rtr("error"))
            return
        server.tell(src.player, server.rtr("wait"))
        for i in range(3):
            server.execute(f'title {player} title "{3 - i}"')
            time.sleep(1)
        server.execute(f'title {player} clear')
        server.execute(f'execute in {data[player]["dim"]} run tp {player} {' '.join([str(i) for i in data[player]["pos"]])}')
        del data[player]
        save_data(server)

    @new_thread("G15T on_death")
    def on_death(server: PluginServerInterface, info: Info):
        ctx = info.content
        player = ctx.split()[0]
        pos = minecraft_data_api.get_player_info(player, "Pos")
        dim = DIMENSIONS[minecraft_data_api.get_player_info(player, "Dimension")]
        data[player] = {"dim": dim, "pos": pos}
        save_data(server)
        quick_c = ""
        if has_command_register:
            quick_c = rtext.RText(" [Getback]", rtext.RColor.yellow).c(rtext.RAction.run_command, "/!!getback")

        display_pos = " ".join([str(int(p)) for p in pos])
        server.tell(player, rtext.RTextList(server.rtr("help", display_pos), quick_c))

    # register
    server.register_command(
        Literal(["!!getback", "!b"])
        .requires(lambda src: src.has_permission(1))
        .runs(getback)
    )

    server.register_event_listener(LiteralEvent("xevents.player_death"), on_death)

    file = server.load_config_simple(
        "data.json", default_config={"minecraft_command_register": False, "data": {}}, echo_in_console=False
    )
    
    data = file["data"]

    has_command_register = file["minecraft_command_register"]


def save_data(server: PluginServerInterface):
    server.save_config_simple({"minecraft_command_register": has_command_register,"data": data}, "data.json")
