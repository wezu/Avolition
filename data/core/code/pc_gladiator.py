'''Avolition 2.0
INFO:
    This is theimplementation of the Gladiator Player Class
    This module is imported by players.py
LICENSE:
    Copyright (c) 2013-2018, wezu (wezu.dev@gmail.com)

    Permission to use, copy, modify, and/or distribute this software for any
    purpose with or without fee is hereby granted, provided that the above
    copyright notice and this permission notice appear in all copies.

    THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
    WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
    MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
    ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
    WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN
    AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING
    OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

'''
from panda3d.core import *
from direct.interval.IntervalGlobal import *

from deferred_render import *
from vfx import Vfx
from vfx import Lightning
from projectile import Projectile
from player import Player

import random

class Gladiator(Player):
    def __init__(self, node):
        model='models/pc/model/male1'
        anims={'action1':'models/pc/anim/male_attack2',
               'action2':'models/pc/anim/male_block',
               'walk':'models/pc/anim/male_run',
               'back':'models/pc/anim/male_run',
               'die':'models/pc/anim/male_die',
               'strafe':'models/pc/anim/male_strafe2',
               'hit':'models/pc/anim/male_hit',
               'idle':'models/pc/anim/male_ready',
               'ready':'models/pc/anim/male_ready2'}
        self.actor_scale=0.025
        sounds={'walk':'walk_fem1',
                'back':'walk_fem1',
                'strafe':'walk_slide',
                'hit':'fem_pain2'}
        play_rates={}
        super().__init__(node, model, anims, self.actor_scale, sounds, play_rates)
        self.actor.loop("idle")

        self.skills={
                    'critical':0.5,
                    'damage':0.5,
                    'speed':0.5,
                    'block':0.5,
                    'regen':0.5,
                    'armor':0.5}
        self.stats={'dmg':20,
                    'critical':50,
                    'speed':100,
                    'block':100,
                    'regen':1,
                    'hp':100}
                    
    def get_sword_dmg(self, charge_time=0):
        base_dmg=15+10*self.skills['damage']   
        charge=pow(charge_time, 1.0+self.skills['damage']*0.5)
        return int(base_dmg+base_dmg*charge)
    
    def get_stats_string(self):
        self.stats={'dmg_min':self.get_sword_dmg(0),
                    'dmg_max':self.get_sword_dmg(2.0),
                    'critical':int(self.skills['critical']*50),
                    'speed':100+int(self.skills['speed']*50),
                    'block':50+int(self.skills['block']*50),
                    'regen':1+int(self.skills['regen']*9),
                    'hp':100+int(self.skills['armor']*100)}

        template= '     SWORD DAMAGE:  {dmg_min}-{dmg_max}\n'
        template+=' CRITICAL HIT(x2):  {critical}%\n'
        template+='       MOVE SPEED:  {speed}%\n'
        template+='   DAMAGE BLOCKED:  {block}%\n'
        template+='     REGENERATION:  {regen}HP/s\n'
        template+='       HIT POINTS:  {hp}'
        return template.format(**self.stats)

    def on_select(self):
        game.audio.play_sound('swing2', self.actor)
        Sequence(self.actor.actorInterval('action1'),self.actor.actorInterval('action2'), Func(self.actor.loop, 'idle')).start()
