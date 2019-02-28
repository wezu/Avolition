'''Avolition 2.0
INFO:
    Visual Effects - pre-rendered particles and lightning rays.
    This version uses shaders to render the effects fast and simple. 
    This module is imported by game.py and player.py
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
import random

class Vfx:
    def __init__(self, texture, loop=False, fps=15.0, frame_size=128):
        tex=loader.load_texture(texture)
        tex.set_magfilter(SamplerState.FT_linear_mipmap_linear )
        tex.set_minfilter(SamplerState.FT_linear_mipmap_linear)
        num_frames= (tex.get_x_size()//frame_size)*(tex.get_y_size()//frame_size)

        self.node=self._make_point()
        shader=Shader.load(Shader.SLGLSL, 'shaders/vfx_v.glsl','shaders/vfx_f.glsl')
        shader_attrib = ShaderAttrib.make(shader)
        shader_attrib = shader_attrib.set_flag(ShaderAttrib.F_shader_point_size, True)
        self.node.set_attrib(shader_attrib)
        self.node.set_transparency(TransparencyAttrib.MDual, 1)
        self.scale=PointerToArrayFloat()
        self.scale.push_back(1.0)
        self.node.set_shader_input('scale', self.scale)
        self.node.set_shader_input('tex', tex)
        self.node.set_shader_input('config', Vec3(frame_size, fps, globalClock.get_frame_time()))

        self.cleanup=[]

        if not loop:
            taskMgr.doMethodLater(num_frames/fps, self.remove,'auto_destruct')

    def setScale(self, *args):
        self.set_scale(*args)

    def set_scale(self, scale):
        self.scale.set_element(0, scale)

    def get_scale(self):
        return self.scale.get_element(0)

    def __getattr__(self,attr):
        return self.node.__getattribute__(attr)

    def remove(self, task=None):
        self.remove_node(task)
        
    def remove_node(self, task=None):
        for cmd in self.cleanup:
            cmd()
        self.node.remove_node()
        self=None

    def _make_point(self, num_points=1):
        aformat = GeomVertexArrayFormat("vertex", 1, GeomEnums.NT_uint8, GeomEnums.C_other)
        format = GeomVertexFormat.register_format(GeomVertexFormat(aformat))
        vdata = GeomVertexData('abc', format, GeomEnums.UH_static)
        vdata.set_num_rows(num_points)
        geom = Geom(vdata)
        p = GeomPoints(Geom.UH_static)
        #p.add_vertex(0)
        p.addNextVertices(num_points)
        geom.add_primitive(p)
        geom.set_bounds(OmniBoundingVolume())
        geom_node = GeomNode('point')
        geom_node.add_geom(geom)
        return forward_render.attach_new_node(geom_node)

class Lightning:
    def __init__(self, start, end, count=5):
        self.start=start
        self.end=end
        self.last_end=end
        self.ray=loader.load_model('vfx/ray')
        self.ray.reparent_to(deferred_render)
        self.ray.set_pos(start)
        self.ray.look_at(end)
        distance=(end-start).length()
        self.ray.set_instance_count(count)
        self.ray.setShader(Shader.load(Shader.SLGLSL, 'shaders/lightning_v.glsl','shaders/lightning_f.glsl'))
        self.ray.set_shader_input('length', distance)
        self.ray.node().set_bounds(OmniBoundingVolume())
        self.ray.hide(BitMask32.bit(13))
        taskMgr.add(self._update, "Lightning_update")
        self.is_hidden=True

    def hide(self):
        self.is_hidden=True
        #self.ray.hide()

    def show(self):
        self.is_hidden=False
        #self.ray.show()

    def _update(self, task):
        if not self.is_hidden:
            self.ray.show()
            delta = min(globalClock.getDt()*50.0, 0.9)
            if int(globalClock.get_frame_time()*10) % 4 ==0:
                self.ray.set_instance_count(random.randint(4,6))
            self.ray.set_pos(self.start)
            self.last_end*=delta
            self.last_end+=self.end*(1.0-delta)

            self.ray.look_at(self.last_end)
            distance=max((self.end-self.start).length(), 1.0)
            self.ray.set_shader_input('length', distance)
        else:
            self.ray.hide()    
        return task.again


