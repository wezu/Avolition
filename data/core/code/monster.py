'''Avolition 2.0
INFO:
    This module handles enemy NPC. Pathfinding is implemented in the Level class (level.py),
    this only controls what the monsters do, and how it looks and sounds
    This module is imported by game.py
LICENSE:
    Copyright (c) 2013-2017, wezu (wezu.dev@gmail.com)

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

import random
from collections import deque

class Monster(DirectObject):
    def __init__(self, model, anims, scale=1.0, move_speed=1.0, sounds=None, play_rates=None,
                hit_frames=(15,), damage=10.0, hp=100):
        self.hit_frames=hit_frames
        self.damage=damage
        self.max_hp=hp
        self.hp=hp
        self.move_speed=move_speed
                
        self.node=deferred_render.attach_new_node('monster')
        #actor
        self.actor=Actor(model, anims)
        self.actor.set_blend(frameBlend = True)
        self.actor.set_scale(scale)
        #self.actor.set_play_rate(-1.0, "back")
        self.actor.set_h(180.0)
        self.actor.flatten_light()
        loader._setTextureInputs(self.actor)
        self.actor.set_transparency(TransparencyAttrib.MNone, 1)
        self.actor.reparent_to(self.node.get_parent())
        self.actor.pose('walk', 0)
        self.actor.node().set_final(True)
        if play_rates:
            for name, rate in play_rates.items():
                self.actor.set_play_rate(rate, name)

        #self.actor.play('walk')

        r=self.actor.get_bounds().get_radius()
        radius =r*0.4
        height =r*0.6
        shape= BulletCapsuleShape(radius, height, ZUp)
        self.collision = game.world_np.attach_new_node(BulletRigidBodyNode('monster'))
        self.collision.node().add_shape(shape, TransformState.makePos(Point3(0, 0, height)))
        self.collision.set_collide_mask(game.bit_mask.monster)
        self.collision.set_python_tag('npc', self)        
        self.collision.set_python_tag('node', self)
        game.world.attach_rigid_body(self.collision.node())

        
        self.attack_detector=game.world_np.attach_new_node(BulletRigidBodyNode('attack'))
        self.attack_detector.node().add_shape(BulletSphereShape(0.5), TransformState.makePos(Point3(0, 0.5, 1)))
        self.attack_detector.set_collide_mask(game.bit_mask.monster_weapon)
        self.attack_detector.node().set_kinematic(True)
        game.world.attach_rigid_body(self.attack_detector.node())
        self.attack_detector.wrt_reparent_to(self.actor)
        self.attack_detector.node().set_transform_dirty()

        self.move_target=None
        self.path=None

        self.pathfind_que=deque()

        taskMgr.add(self.update, "monster_update")
        taskMgr.doMethodLater(1.0, self.update_ai,'monster_update_ai')
    
    def on_hit(self, damage):
        self.hp-=damage
        if self.hp<=0:
            self.on_death()
        else:
            if 'hit' in self.actor.get_anim_names():
                self.actor.play('hit')        
                
    def on_death(self):
        if 'die' in self.actor.get_anim_names():
            self.actor.play('die')        
        game.dead_monsters.add(self)    
        game.monsters.discard(self)
        
    def respawn(self, pos):
        self.hp=int(self.max_hp)
        self.actor.stop()
        self.set_pos(pos)
    
    def __getattr__(self,attr):
        return self.node.__getattribute__(attr)

    def update_ai(self, task):
        if self.hp<=0:
            return task.again
        #am I attacking?
        if self.actor.get_current_anim() in ('attack', 'hit', 'die'):
            return task.again
        #do I see the player?
        from_point=self.node.get_pos(render)
        to_point=game.pc.node.get_pos(render)
        mask=game.bit_mask.floor|game.bit_mask.wall|game.bit_mask.player
        hit=game.ray_test(from_point+Point3(0,0,1), to_point+Point3(0,0,1), mask)
        if hit:
            hit_node=NodePath().any_path(hit[1])
            if hit_node.has_python_tag('pc'):
                #print('I see player!')
                self.move_target=to_point
                self.path=None
            else:
                self.move_target=None
                if not self.path:
                    game.level.request_path(from_point, to_point, self.pathfind_que)
                #print('Player gonne!')
        #else:
        #    print ("I'm lost?")
        return task.again

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
            t = min(dt*100.0/delta, 1.0)
            new_hpr = orig_hpr + (target_hpr - orig_hpr) * t
            node.set_hpr(new_hpr)

    def update(self, task):
        if self.hp<=0:
            return task.again

        dt = globalClock.getDt()
        self.new_anim=None
        self.collision.set_pos(self.node.get_pos())
        self.actor.set_pos(self.node.get_pos())

        #do collisions
        result=game.world.contact_test(self.attack_detector.node(), True)
        if result.get_num_contacts() >0:
            for contact in result.get_contacts():
                hit_node=NodePath().any_path(contact.get_node1())
                if hit_node.has_python_tag('pc'):
                    pc=hit_node.get_python_tag('pc')
                    if self.node.get_distance(pc.node)<0.9:
                        self.node.set_y(self.node, -self.move_speed*dt*3.0)
                    elif self.actor.get_current_anim() != 'attack':
                        self.actor.play('attack')
                    else:
                        if self.actor.get_current_frame('attack') in self.hit_frames:
                            pc.on_hit()                            
        
        #movement
        if self.actor.get_current_anim() != 'attack':
            if self.move_target:
                self.node.heads_up(self.move_target)                
                self.node.set_y(self.node, self.move_speed*dt)
                if self.actor.get_current_anim() != 'walk':
                    self.actor.play('walk')
            elif self.path:
                target=self.path[-1]
                distance=(self.node.get_pos(render)-target).length()
                if distance <0.5:
                    target=self.path.pop()
                self.node.heads_up(target)
                self.node.set_y(self.node, self.move_speed*dt)
                if self.actor.get_current_anim() != 'walk':
                    self.actor.play('walk')
            elif len(self.pathfind_que) > 0:
                self.path=self.pathfind_que.popleft()
                self.pathfind_que.clear()

        #turn a bit?
        self._turn_to(self.actor, self.node, dt)
        
        return task.again
