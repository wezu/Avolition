'''Avolition 2.0
INFO:
    This module controls the camera movement.
    The player avatar moves in the same direction that the camera looks,
    so this class in part also controls the PC movement.
    This module is imported by game.py
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
from direct.showbase.DirectObject import DirectObject
import math

__all__ = ['CameraControler']

sign = lambda x: math.copysign(1, x)

class CameraControler (DirectObject):
    '''Class to control the camera.
    Allows to rotate 360deg around a point, zoom in and out,
    and change the viewing angle of the camera.
    '''
    def __init__(self, pos=(0,0,10.0), offset=(0, 10, 10), speed=1.0,
                 zoom_speed=1.0, limits=(150.0, 650.0, -50, 40.0) ):
        self.node  = deferred_render.attach_new_node("node")
        self.root  = self.node.attach_new_node("root")
        self.root.set_pos(render, pos)
        self.gimbal  = self.root.attach_new_node("gimbal")
        base.camera.set_pos(render, offset)
        base.camera.look_at(self.root)
        base.camera.wrt_reparent_to(self.gimbal)

        self.initial_pos=pos
        self.initial_offset=offset

        self.last_mouse_pos=Vec2(0,0)
        self.speed=speed*200.0
        self.move_speed=speed*10.0
        self.zoom_speed=zoom_speed*50.0
        self.zoom = 0.0
        self.limits=limits[:2]
        self.max_p=limits[2:4]

        self.active=False
        self.was_active_last_frame=False

        self.key_map = {'rotate': False, 'forward':False, 'back':False,
                        'left':False, 'right':False,
                        'r_left':False, 'r_right':False}
        taskMgr.add(self.update, "camcon_update", sort=-151)

    def bind_keys(self, rotate='mouse1', zoom_in='wheel_up', zoom_out='wheel_down'):
        ''' Make the camera respond to key press/mouse move'''
        self.ignoreAll()
        self.accept(rotate, self.key_map.__setitem__, ['rotate', True])
        self.accept(rotate+'-up', self.key_map.__setitem__, ['rotate', False])
        self.accept(zoom_in, self.zoom_control,[1.0])
        self.accept(zoom_out,self.zoom_control,[-1.0])

        self.accept('q', self.key_map.__setitem__, ['r_left', True])
        self.accept('q-up', self.key_map.__setitem__, ['r_left', False])
        self.accept('e', self.key_map.__setitem__, ['r_right', True])
        self.accept('e-up', self.key_map.__setitem__, ['r_right', False])


        half_x=base.win.getXSize()//2
        half_y=base.win.getYSize()//2
        base.win.movePointer(0, half_x, half_y)

    def reset(self):
        '''Reset the position and rotation of the camera'''
        self.root.set_pos(render, self.initial_pos)
        self.node.set_hpr(0,0,0)
        self.gimbal.set_hpr(0,0,0)
        base.camera.set_pos(render, self.initial_offset)
        base.camera.look_at(self.root)

    def set_rotation_speed(self, speed):
        self.speed=(0.1+speed)*250.0
        Config.set('control','camera-speed', str(speed))

    def set_zoom_speed(self, speed):
        self.zoom_speed=(0.1+speed)*99.0
        Config.set('control','zoom-speed', str(speed))

    def zoom_control(self, amount):
        self.zoom+=amount*self.zoom_speed
        self.zoom=min(max(self.zoom, -6.0*self.zoom_speed), 6.0*self.zoom_speed)

    def set_active(self, active=True):
        half_x=base.win.getXSize()//2
        half_y=base.win.getYSize()//2
        base.win.movePointer(0, int(half_x), int(half_y))
        self.last_mouse_pos=Point2(0,0)
        self.active=active

    def update(self, task):
        if not self.active:
            self.was_active_last_frame=False
            return task.again
        if not self.was_active_last_frame:
            self.was_active_last_frame=True
            return task.again
        dt = globalClock.getDt()

        if self.key_map['r_left']:
            self.node.set_h(self.node.get_h()+50.0*dt)
        elif self.key_map['r_right']:
            self.node.set_h(self.node.get_h()-50.0*dt)

        if base.mouseWatcherNode.has_mouse():
            if self.zoom != 0.0:
                distance=base.camera.get_distance(self.node)
                if (distance > self.limits[0] and self.zoom >0.0) or (distance < self.limits[1] and self.zoom < 0.0):
                    zoom_speed=self.zoom*dt
                    base.camera.set_y(base.camera, zoom_speed)
                    zoom_speed*=4.0
                    if self.zoom > 0.1:
                        self.zoom-=zoom_speed
                    elif self.zoom < -0.1:
                        self.zoom-=zoom_speed
                    else:
                        self.zoom=0.0
            m_pos=base.mouseWatcherNode.get_mouse()
            delta = m_pos- self.last_mouse_pos
            self.last_mouse_pos = Vec2(m_pos)

            p=self.gimbal.get_p()- delta[1]*self.speed*30.0*dt
            self.gimbal.set_p(min(max(p, self.max_p[0]), self.max_p[1]))
            self.node.set_h(self.node.get_h()- delta[0]*self.speed*80.0*dt)

            if abs(self.last_mouse_pos.x)>0.9 or abs(self.last_mouse_pos.y)>0.9:
                half_x=base.win.getXSize()//2
                half_y=base.win.getYSize()//2
                base.win.movePointer(0, half_x, half_y)
                self.last_mouse_pos=Point2(0,0)
            #move croshair away
            if self.gimbal.get_p()>0.0:
                offset=self.gimbal.get_p()*0.015
                pos=pixel2d.get_relative_point(render2d, (0,0,0.18+offset))
                game.gui.croshair.set_pos(pos)
            else:
                pos=pixel2d.get_relative_point(render2d, (0,0,0.18))
                game.gui.croshair.set_pos(pos)
        else:
            half_x=base.win.getXSize()//2
            half_y=base.win.getYSize()//2
            base.win.movePointer(0, half_x, half_y)
            self.last_mouse_pos=Point2(0,0)
        return task.again
