'''Avolition 2.0
INFO:
    This module provides a basic Player class that allows the player to control an avatar with mouse and keys,
    it relies on the camera control in camera.py to look (and eventually move) in the right direction.
    The player classes actually used only need to re-implement the 'actions' functions
    (on_start_action*(), on_continue_action*(), on_end_action*() and on_break_action*())
    and add class specific functions (like lightning for the witch)
    This module is imported by pc_*.py
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
from panda3d.bullet import *
from direct.showbase.DirectObject import DirectObject
from direct.showbase.PythonUtil import fitSrcAngle2Dest
from direct.interval.IntervalGlobal import *
from direct.actor.Actor import Actor

from deferred_render import *
from vfx import Vfx
from vfx import Lightning
from projectile import Projectile

import random

__all__ = ['Rogue', 'Witch', 'Gladiator', 'Druid']

class Player(DirectObject):
    def __init__(self, node, model, anims, scale, sounds=None, play_rates=None, hw_skinning=True):
        self.node=node
        #actor
        self.actor=Actor(model, anims)
        self.actor.set_blend(frameBlend = True)
        if play_rates:
            for name, rate in play_rates.items():
                self.actor.set_play_rate(rate, name)
        if hw_skinning:
            attr = ShaderAttrib.make(Shader.load(Shader.SLGLSL, 'shaders/actor_v.glsl', 'shaders/geometry_f.glsl'))
            attr = attr.setFlag(ShaderAttrib.F_hardware_skinning, True)
            self.actor.setAttrib(attr)

        self.actor.set_scale(scale)
        self.actor.set_play_rate(-1.0, "back")
        #self.actor.set_h(180.0)

        loader._setTextureInputs(self.actor)
        self.actor.set_transparency(TransparencyAttrib.MNone, 1)

        self.actor.reparent_to(self.node.get_parent())

        r=self.actor.get_bounds().get_radius()
        radius =r*0.4
        height =r*0.8
        shape= BulletCapsuleShape(radius, height, ZUp)
        self.collision = game.world_np.attach_new_node(BulletRigidBodyNode('pc'))
        self.collision.node().add_shape(shape, TransformState.makePos(Point3(0, 0, r)))
        self.collision.set_collide_mask(game.bit_mask.player)
        self.collision.set_python_tag('pc', self)
        self.collision.set_python_tag('node', self)

        game.world.attach_rigid_body(self.collision.node())


        self.move_speed=4.0
        self.key_map = {'forward':False, 'back':False,
                        'left':False, 'right':False,
                        'action1':False, 'action2':False}

        #self.bind_keys()
        self.wait_for_anim_end=False
        self.health=100
        self.energy=100
        self.is_hit=False
        self.skills={}
        self.sounds=sounds
        self.last_sound=None
        
    def get_name(self):
        return self.__class__.__name__
        
    def bind_keys(self, left='a', right='d', forward='w', back='s', action1='mouse1',  action2='mouse3'):
        """Enable controls and bind keys """
        self.ignore_all()
        self.accept(left, self.key_map.__setitem__, ['left', True])
        self.accept(left+'-up', self.key_map.__setitem__, ['left', False])
        self.accept(right, self.key_map.__setitem__, ['right', True])
        self.accept(right+'-up', self.key_map.__setitem__, ['right', False])
        self.accept(forward, self.key_map.__setitem__, ['forward', True])
        self.accept(forward+'-up', self.key_map.__setitem__, ['forward', False])
        self.accept(back, self.key_map.__setitem__, ['back', True])
        self.accept(back+'-up', self.key_map.__setitem__, ['back', False])

        self.accept(action1, self.key_map.__setitem__, ['action1', True])
        self.accept(action1+'-up', self.key_map.__setitem__, ['action1', False])
        self.accept(action2, self.key_map.__setitem__, ['action2', True])
        self.accept(action2+'-up', self.key_map.__setitem__, ['action2', False])
        taskMgr.add(self.update, "player_update")


    def on_hit(self, damage=0):
        """ This function needs to be called when the player is hit"""
        self.is_hit=True
        if self.actor.get_current_anim() == 'hit':
            self.is_hit=False
            return
        hit_vfx=Vfx('vfx/blood_red.png', loop=False, fps=60.0)
        hit_vfx.set_scale(1.5)
        pos=self.node.get_pos(render)
        pos.z=0.7
        hit_vfx.set_pos(pos)

    #these functions should be re-implemented in sub classes
    #they are called automatically in the update task
    def on_start_action1(self):
        pass
    def on_continue_action1(self, dt):
        pass
    def on_end_action1(self):
        pass
    def on_break_action1(self):
        pass
    def on_start_action2(self):
        pass
    def on_continue_action2(self, dt):
        pass
    def on_end_action2(self):
        pass
    def on_break_action2(self):
        pass
    #these also need to be defined per character class
    def get_stats_string(self):
        return ''
    def on_select(self):
        pass
        
    def set_skills(self, skill1, skill2, value):
        self.skills[skill1]=value
        self.skills[skill2]=1.0-value
        
    def _turn_to(self, node, target, dt):
        orig_hpr = node.get_hpr()
        target_hpr = target.get_hpr()
        # Make the rotation go the shortest way around.
        orig_hpr = Vec3(fitSrcAngle2Dest(orig_hpr[0], target_hpr[0]),
                         fitSrcAngle2Dest(orig_hpr[1], target_hpr[1]),
                         fitSrcAngle2Dest(orig_hpr[2], target_hpr[2]))

        # How far do we have to go from here?
        delta = max(abs(target_hpr[0] - orig_hpr[0]),
                    abs(target_hpr[1] - orig_hpr[1]),
                    abs(target_hpr[2] - orig_hpr[2]))
        if delta != 0:
            # Figure out how far we should rotate in this frame, based on the
            # distance to go, and the speed we should move each frame.
            # If we reach the target, stop there.
            t = min(dt*300.0/delta, 1.0)
            new_hpr = orig_hpr + (target_hpr - orig_hpr) * t
            node.set_hpr(new_hpr)

    def update(self, task):
        dt = globalClock.getDt()
        self.new_anim=None
        last_pos=self.node.get_pos()
        #check for anim finish
        anim=self.actor.get_current_anim()
        #run sounds
        if anim in self.sounds:
            if game.audio.is_playing(self.last_sound):
                if self.last_sound.get_name() != game.audio.sounds[self.sounds[anim]].get_name():
                    self.last_sound=game.audio.play_sound(self.sounds[anim], self.node)
            else:
                self.last_sound=game.audio.play_sound(self.sounds[anim], self.node)
        if self.wait_for_anim_end:
            if anim != None:
                #print(anim)
                return task.again
            else:
                self.wait_for_anim_end=False

        #check for hits
        if self.is_hit:
           self.new_anim='hit'
           self.is_hit=False
           self.wait_for_anim_end=True
        else:
            #check for actions
            if self.key_map['action1'] and not self.key_map['action2']:
                self.new_anim='action1'
            elif self.key_map['action2'] and not self.key_map['action1']:
                self.new_anim='action2'
            else: #check/do for movement
                if self.key_map['forward']:
                    self.node.set_y(self.node,-self.move_speed*dt)
                    self.new_anim='walk'
                elif self.key_map['back']:
                    self.node.set_y(self.node,self.move_speed*dt)
                    self.new_anim='back'
                if self.key_map['left']:
                    self.node.set_x(self.node,self.move_speed*dt*0.25)
                    if self.new_anim is None:
                        self.new_anim='strafe'
                elif self.key_map['right']:
                    self.node.set_x(self.node,-self.move_speed*dt*0.25)
                    if self.new_anim is None:
                        self.new_anim='strafe'
                #sync collisions and actor
                self.collision.set_pos(self.node.get_pos())
                self.actor.set_pos(self.node.get_pos())

        #execute actions:
        if self.new_anim=='action1' and anim != 'action1':
            self.on_start_action1()
        elif self.new_anim=='action1' and anim == 'action1':
            self.on_continue_action1(dt)
        elif self.new_anim=='hit' and anim == 'action1':
            self.on_break_action1()
        elif self.new_anim!='action1' and anim == 'action1':
            self.on_end_action1()
        elif self.new_anim=='action2' and anim != 'action2':
            self.on_start_action2()
        elif self.new_anim=='action2' and anim == 'action2':
            self.on_continue_action2(dt)
        elif self.new_anim=='hit' and anim == 'action2':
            self.on_break_action2()
        elif self.new_anim!='action2' and anim == 'action2':
            self.on_end_action2()

        #run anims:
        if self.new_anim:
            #change hpr
            self._turn_to(self.actor, self.node, dt)
            if anim != self.new_anim:
                self.actor.play(self.new_anim)
        else:
            if anim != 'idle':
                self.actor.play('idle')
                if game.audio.is_playing(self.last_sound):
                    self.last_sound.stop()

        #do movement collisions
        result=game.world.contact_test(self.collision.node(), True)
        if result.get_num_contacts() >0:
            for contact in result.get_contacts():
                hit_node=NodePath().any_path(contact.get_node1())
                if hit_node.get_collide_mask() != game.bit_mask.monster_weapon:
                    self.node.set_pos(last_pos)
                    break

        return task.again

