'''Avolition 2.0
INFO:
    Creates and manages a projectile.
    This module is imported by player.py
LICENSE:
    Copyright (c) 2018, wezu (wezu.dev@gmail.com)

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

class Projectile:
    def __init__(self, visual, size, pos, hpr, speed, mask, on_hit_cmd, time_to_live=15.0):
        """
        Creates a sphere projectile with size radius,
        visual is a node (or other object with a set_pos function) moving with the projectile
        pos is the starting position
        hpr is the initial rotation (projectile moves down the Y axis)
        speed is the distance traveled in 1 sec.
        mask is a collision bitmask
        on_hit_cmd is a function executed when the projectile hits something,
        the hit node, pos and the projectile itself are passed to that function (on_hit_cmd(hit_node, hit_pos, self))
        """
        self.speed=speed
        self.on_hit_cmd=on_hit_cmd
        self.life=time_to_live
        self.visual=visual
        self.sphere = game.world_np.attach_new_node(BulletRigidBodyNode('Ground'))
        shape=BulletSphereShape(size)
        shape.set_margin(0.0)
        self.sphere.node().add_shape(shape)
        self.sphere.set_pos(*pos)
        self.sphere.set_hpr(*hpr)
        self.sphere.set_collide_mask(mask)
        game.world.attach_rigid_body(self.sphere.node())        

        self.task=taskMgr.add(self.update, "projectile_update")

    def remove(self):
        self.visual.remove_node()
        game.world.remove(self.sphere.node())
        self.sphere.remove_node()
        taskMgr.remove(self.task)
        
        self.speed=None
        self.on_hit_cmd=None
        self.life=None
        self.visual=None
        self.sphere= None
        self.task=None
        
    def update(self, task):
        dt = globalClock.getDt()
        self.life-=dt
        if self.life<0:
            self.remove()
            return task.done
        self.sphere.set_y(self.sphere, self.speed*dt)
        self.visual.set_pos(self.sphere.get_pos(render))
        #collision
        result=game.world.contact_test(self.sphere.node(), True)
        if result.get_num_contacts() >0:
            for contact in result.get_contacts():
                mpoint = contact.get_manifold_point()
                hit_node=contact.get_node1()
                hit_pos=mpoint.get_position_world_on_a()

                self.on_hit_cmd(hit_node, hit_pos, self)

                return task.done
        return task.again
