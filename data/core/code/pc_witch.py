'''Avolition 2.0
INFO:
    This is theimplementation of the Witch Player Class
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


class Witch(Player):
    def __init__(self, node):
        model='models/pc/model/fem1'
        anims={'action1':'models/pc/anim/female_attack1',
               'action2':'models/pc/anim/female_idle',
               'action2_done':'models/pc/anim/female_attack2',
               'walk':'models/pc/anim/female_run',
               'back':'models/pc/anim/female_run',
               'die':'models/pc/anim/female_die',
               'strafe':'models/pc/anim/female_strafe',
               'hit':'models/pc/anim/female_hit',
               'idle':'models/pc/anim/female_idle'}
        self.actor_scale=0.026
        sounds={'walk':'walk_fem1',
                'back':'walk_fem1',
                'strafe':'walk_slide',
                'hit':'fem_pain2'}
        play_rates={'action2':2.0,
                   'action2_done':1.5}
        super().__init__(node, model, anims, self.actor_scale, sounds, play_rates)
        self.actor.loop("idle")
              
        self.lightning=Lightning(Point3(0,0,0), Point3(0,10,1))
        self.lightning.hide()

        self.plasma_charge_time=0
        self.skills={'static':0.5,
                    'rapid':0.5,
                    'thunder':0.5,
                    'lightning':0.5,
                    'damage':0.5,
                    'blast':0.5}
                    
        self.stats={'dmg':20,
                    'far_dmg':50,
                    'near_dmg':100,
                    'blast':100,
                    'hp':100}

    def get_bolt_dmg(self, charge_time=0):
        base_dmg=10   
        charge=(1.5+charge_time)*self.skills['static']
        charge+=pow((1.0+(charge_time/2.0)), 2)*self.skills['rapid']
        return int((base_dmg+base_dmg*charge)*(self.skills['damage']+1.0))
    
    def get_stats_string(self):
        self.stats={'bolt_dmg1':self.get_bolt_dmg(0),
                    'bolt_dmg2':self.get_bolt_dmg(1.0),
                    'bolt_dmg3':self.get_bolt_dmg(2.0),
                    'bolt_blast':0.1+self.skills['blast']*2.4,
                    'lightning_dmg':2.0*(pow(2.0*(2.0+self.skills['thunder']), 2)),
                    'lightning_charge_rate':1.0+self.skills['thunder']*2.5,     
                    'hp':100
                    } 
        
        template= '  LIGHTNING DAMAGE:  {lightning_dmg:.1f}/s\n'
        template+='LIGHTNING RECHARGE:  {lightning_charge_rate:.1f}s\n'
        template+='   BOLT BLAST SIZE:  {bolt_blast:.1f}m\n'
        template+=' MAGIC BOLT DAMAGE:  {bolt_dmg1:<6}{bolt_dmg2:<6}{bolt_dmg3:<6}\n'
        template+='       (charge)      0%    50%   100%'
        return template.format(**self.stats)

    def on_select(self):
        self.lightning.last_end=Point3(0.0, 0.0, .5)
        self.lightning.end=Point3(1.8, -4.5, 1.2)
        self.lightning.start=render.get_relative_point(self.actor, Point3(0,-0.2,0.75)/self.actor_scale)
        self.temp_light = SphereLight(color=(0.1,0.2,1.0), pos=(0,0, 1.5), radius=15.0, shadow_size=0)
        Sequence(Wait(0.2), Func(self.lightning.show)).start()
        Sequence(self.actor.actorInterval('action1'),Func(self.actor.loop, 'idle'), Func(self.lightning.hide), Func(self.temp_light.remove)).start()
        game.audio.play_sound(random.choice(['thunder2','thunder3']), self.actor)


    def get_hand_pos(self):
        return render.get_relative_point(self.actor, Point3(0,-0.3,0.93)/self.actor_scale)

    def on_plasma_hit(self, hit_node, hit_pos, projectile):
        #print(hit_node)
        #print(hit_pos)
        scale=projectile.visual.get_scale()
        pos=projectile.visual.get_pos(render)
        game.audio.play_sound('plasma_hit', None, pos=pos)
        hit_vfx=Vfx('vfx/m_blast.png', loop=False, fps=60.0)
        hit_vfx.set_pos(pos)
        self.temp_light = SphereLight(color=(0.1,0.2,1.0), pos=pos, radius=15.0, shadow_size=0)
        Sequence(LerpFunc(hit_vfx.set_scale, fromData=1.0, toData=3.0*scale, duration=0.5), Func(self.temp_light.remove)).start()
        #Sequence(LerpScaleInterval(hit_vfx, 0.5, 9.0, 1.0), Func(self.temp_light.remove)).start()
        projectile.remove()

    def update_lightning(self):
        hit=game.camera_ray_test(game.bit_mask.weapon_ray)
        if hit:
            self.lightning.end=hit.pos
            self.lightning.start=render.get_relative_point(self.actor, Point3(0,-0.2,0.7)/self.actor_scale)
            self.lightning.show()
            try:
                self.lightning_light.pos=(Point3(self.lightning.end)+self.lightning.start)*0.5
                self.lightning_light.radius=(Point3(self.lightning.end)-self.lightning.start).length()
                self.lightning_light.color=(random.uniform(0.0, 0.2), random.uniform(0.0, 0.2), random.uniform(0.9, 1.0))
            except:
                l_pos=(Point3(self.lightning.end)+self.lightning.start)*0.5
                r=(Point3(self.lightning.end)-self.lightning.start).length()
                self.lightning_light = SphereLight(color=(0.1,0.2,0.9), pos=l_pos, radius=r, shadow_size=0)
                self.lightning.last_end=hit.pos
        else:
            self.lightning.hide()

    #action 1 lightning
    def on_start_action1(self):
        self.update_lightning()
        self.lightning_sfx=game.audio.play_sound(random.choice(['thunder2','thunder3']), self.node)

    def on_continue_action1(self, dt):
        max_frame=self.actor.get_num_frames('action1')
        frame=self.actor.get_current_frame('action1')
        if frame >= max_frame-1:
            self.actor.play('action1', fromFrame = max_frame//2)
        self.update_lightning()

    def on_end_action1(self):
        self.lightning.hide()
        try:
            del self.lightning_light
        except:
            pass

    def on_break_action1(self):
        self.key_map['action1']=False
        self.on_end_action1()

    #action 2 plasma ball
    def on_start_action2(self):
        if self.plasma_charge_time == 0:
            self.plasma_charge_sfx=game.audio.play_sound('plasma_charge', self.node)
            self.plasma_vfx=Vfx('vfx/plasm2.png', loop=True, fps=60.0, frame_size=128)
            self.plasma_vfx.set_scale(1.0)
            self.plasma_vfx.set_pos(self.get_hand_pos())
            self.plasma_light = SphereLight(color=(0.1,0.2,0.9), pos=self.get_hand_pos(), radius=5.0, shadow_size=0)
            self.plasma_light.attach_to(self.plasma_vfx.node)
        else:
            self.plasma_charge_time = 0

    def on_continue_action2(self, dt):
        self.plasma_charge_time+=dt*4.0
        self.plasma_charge_time=min(self.plasma_charge_time, 2.0)
        max_frame=self.actor.get_num_frames('action2')
        frame=self.actor.get_current_frame('action2')
        if frame >= max_frame-1:
            self.actor.play('action2')
        self.plasma_vfx.set_pos(self.get_hand_pos())
        self.plasma_vfx.set_scale(1.0+self.plasma_charge_time)

    def on_end_action2(self):
        self.plasma_charge_sfx.stop()
        self.new_anim='action2'
        self.actor.play('action2_done')
        self.wait_for_anim_end=True

        hit=game.camera_ray_test(game.bit_mask.weapon_ray)
        if hit:
            self.plasma_vfx.look_at(hit.pos)
            game.audio.play_sound('plasma_fly_noloop', self.plasma_vfx.node)
            plasma=Projectile(visual=self.plasma_vfx,
                              size=0.2,
                              pos=self.plasma_vfx.get_pos(render),
                              hpr=self.plasma_vfx.get_hpr(render),
                              speed=5.0+5.0*self.plasma_charge_time,
                              mask=game.bit_mask.weapon,
                              on_hit_cmd=self.on_plasma_hit)
        else:
            self.plasma_vfx.remove()

        self.plasma_charge_time=0

    def on_break_action2(self):
        self.key_map['action1']=False
        self.plasma_vfx.remove()

