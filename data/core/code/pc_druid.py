'''Avolition 2.0
INFO:
    This is theimplementation of the Druid Player Class
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


class Druid(Player):
    def __init__(self, node):
        model='models/pc/model/male2'
        anims={'action1':'models/pc/anim/male2_aura',
               'action2':'models/pc/anim/male2_attack',
               'walk':'models/pc/anim/male2_walk',
               'back':'models/pc/anim/male2_walk',
               'die':'models/pc/anim/male2_die',
               'strafe':'models/anim/pc/male2_strafe',
               'hit':'models/pc/anim/male2_hit',
               'idle':'models/pc/anim/male2_idle'}
        self.actor_scale=0.023
        sounds={'walk':'walk_fem1',
                'back':'walk_fem1',
                'strafe':'walk_slide',
                'hit':'fem_pain2'}
        play_rates={'action1':2.0}
        super().__init__(node, model, anims, self.actor_scale, sounds, play_rates)
        self.actor.loop("idle")
        self.skills={
                    'warp':0.5,
                    'phase':0.5,
                    'volcanic':0.5,
                    'fire':0.5,
                    'magma':0.5,
                    'burning':0.5
                    }
        self.stats={'magma_dmg':20,
                    'magma_num':3,
                    'magma_life':5.0,
                    'magma_size':100,
                    'tele_speed':100,
                    'tele_cool':1.0,
                    'hp':100}

    def get_stats_string(self):
        self.stats={'magma_dmg':15+int(self.skills['burning']*25),
                    'magma_num':1+int(self.skills['magma']*5),
                    'magma_life':round(3.0+self.skills['fire']*6.0, 2),
                    'magma_size':50+int(self.skills['volcanic']*100),
                    'tele_speed':50+int(self.skills['warp']*100),
                    'tele_cool':round(5.0-self.skills['phase']*4.5, 2),
                    'hp':100}
        template= '     MAGMA DAMAGE:  {magma_dmg}/s\n'
        template+='  MAX MAGMA BLOBS:  {magma_num}\n'
        template+='   MAGMA DURATION:  {magma_life}s\n'
        template+='       MAGMA SIZE:  {magma_size}%\n'
        template+='   TELEPORT SPEED:  {tele_speed}%\n'
        template+='TELEPORT COOLDOWN:  {tele_cool}s'
        return template.format(**self.stats)

    def on_select(self):
        game.audio.play_sound('forcefield4', self.actor)
        Sequence(self.actor.actorInterval('action2', playRate=1.0), Func(self.actor.loop, 'idle')).start()
        pos=self.actor.get_pos()+Point3(-0.6, -0.4, 1.6)
        vfx=Vfx('vfx/tele2.png', loop=False, fps=40.0)
        vfx.set_pos(pos)
        #LerpFunc(vfx.set_scale, fromData=5.0, toData=2.0, duration=0.7).start()
        self.temp_light = SphereLight(color=(0.1,0.2,1.0), pos=pos, radius=5.0, shadow_size=0)
        Sequence(LerpFunc(vfx.set_scale, fromData=5.0, toData=2.0, duration=0.7), Func(self.temp_light.remove)).start()
