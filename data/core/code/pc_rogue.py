'''Avolition 2.0
INFO:
    This is theimplementation of the Rogue Player Class
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

class Rogue(Player):
    def __init__(self, node):
        model='models/pc/model/fem2'
        anims={'action1':'models/pc/anim/female2_arm',
               'action1_done':'models/pc/anim/female2_fire',
               'action2':'models/pc/anim/female2_run2',
               'walk':'models/pc/anim/female2_run',
               'back':'models/pc/anim/female2_run',
               'die':'models/pc/anim/female2_die',
               'strafe':'models/pc/anim/female2_strafe',
               'hit':'models/pc/anim/female2_hit',
               'idle':'models/pc/anim/female2_idle'}
        self.actor_scale=0.026
        sounds={'walk':'walk_fem1',
                'back':'walk_fem1',
                'strafe':'walk_slide',
                'hit':'fem_pain2'}
        play_rates={'action2':2.0,
                   'action2_done':1.5}
        super().__init__(node, model, anims, self.actor_scale, sounds, play_rates)
        self.actor.loop("idle")
        
        self.skills={'prowess':0.5,
                     'finesse':0.5,
                     'cripple':0.5,
                     'bleed':0.5,
                     'pierce':0.5,
                     'barbs':0.5}
                    
        self.stats={'dmg':20,
                    'slow':50,
                    'bleed':100,
                    'pierce':100,
                    'barbs':1,
                    'hp':100}
                    
    def get_arrow_dmg(self, charge_time=0):
        base_dmg=10+5*self.skills['prowess']   
        charge=charge_time*1.5+self.skills['prowess']
        return int(base_dmg+base_dmg*charge)
        
    def get_stats_string(self):
        self.stats={'dmg_min':self.get_arrow_dmg(0),
                    'dmg_max':self.get_arrow_dmg(2.0),
                    'critical':25+int(self.skills['finesse']*50),
                    'slow':int(self.skills['cripple']*100),
                    'bleed':int(self.skills['bleed']*100),
                    'pierce':int(self.skills['pierce']*50),
                    'barbs':int(self.skills['barbs']*50),
                    'hp':100}

        template= '     ARROW DAMAGE:  {dmg_min}-{dmg_max}\n'
        template+='    EFFECT CHANCE:  {critical}%\n'
        template+='  SLOW DOWN ENEMY:  {slow}%\n'
        template+=' DAMAGE OVER TIME:  {bleed}%\n'
        template+=' PASS THRUE ENEMY:  {pierce}%\n'
        template+='       DOUBLE HIT:  {barbs}%'
        return template.format(**self.stats)

    def on_select(self):
        game.audio.play_sound('draw_bow2', self.actor)
        self.actor.play('action1')
        Sequence(Wait(1.0),Func(game.audio.play_sound, 'fire_arrow3', self.actor), Func(self.actor.play, 'action1_done'),Wait(1.0),Func(self.actor.loop, 'idle')).start()
