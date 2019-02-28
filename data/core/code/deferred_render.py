'''
INFO:
    This module implements a deferred rendering pipeline.
    It was not originally written for the Avolition 2.0 project
    It is also available in stand-alone form here: https://github.com/wezu/p3d_auto_deferred_shader
    This module is imported by game.py
LICENSE:
    Copyright (c) 2017-2018, wezu (wezu.dev@gmail.com)

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
import sys
import math
from functools import lru_cache
from direct.showbase.DirectObject import DirectObject
from panda3d.core import *
import builtins

__author__ = "wezu"
__copyright__ = "Copyright 2017"
__license__ = "ISC"
__version__ = "0.13a1"
__email__ = "wezu.dev@gmail.com"
__all__ = ['SphereLight', 'ConeLight', 'SceneLight', 'DeferredRenderer']


class DeferredRenderer(DirectObject):
    """
    DeferredRenderer is a singelton class that takes care of rendering
    It installs itself in the buildins,
    it also creates a deferred_render and forward_render nodes.
    """

    def __init__(self, filter_setup=None, shading_setup=None, shadows=None, scene_mask=1, light_mask=2):
        # check if there are other DeferredRenderer in buildins
        if hasattr(builtins, 'deferred_renderer'):
            raise RuntimeError('There can only be one DeferredRenderer')

        builtins.deferred_renderer = self
        # template to load the shaders by name, without the directory and
        # extension
        self.f = 'shaders/{}_f.glsl'
        self.v = 'shaders/{}_v.glsl'
        # last known window size, needed to test on window events if the window
        # size changed
        self.last_window_size = (base.win.get_x_size(), base.win.get_y_size())

        self.shadow_size=shadows
        self.attached_lights={}
        self.modelMask = scene_mask
        self.lightMask = light_mask

        # install a wrapped version of the loader in the builtins
        builtins.loader = WrappedLoader(builtins.loader)
        loader.texture_shader_inputs = [{'input_name': 'tex_diffuse',
                                         'stage_modes': (TextureStage.M_modulate, TextureStage.M_modulate_glow, TextureStage.M_modulate_gloss),
                                         'default_texture': loader.load_texture('tex/def_diffuse.png')},
                                        {'input_name': 'tex_normal',
                                         'stage_modes': (TextureStage.M_normal, TextureStage.M_normal_height, TextureStage.M_normal_gloss),
                                         'default_texture': loader.load_texture('tex/def_normal.png')},
                                        {'input_name': 'tex_material',  # Shine Height Alpha Glow
                                         # something different
                                         'stage_modes': (TextureStage.M_selector,),
                                         'default_texture': loader.load_texture('tex/def_material.png')}]
        # set up the deferred rendering buffers
        self.shading_setup = shading_setup
        self._setup_g_buffer(self.shading_setup)

        # post process
        self.filter_buff = {}
        self.filter_quad = {}
        self.filter_tex = {}
        self.filter_cam = {}

        self.cube_tex=loader.load_cube_map('tex/cube/sky_#.png')
        tex_format=self.cube_tex.get_format()
        if tex_format == Texture.F_rgb:
            tex_format = Texture.F_srgb
        elif tex_format == Texture.F_rgba:
            tex_format = Texture.F_srgb_alpha
        self.cube_tex.set_format(tex_format)
        self.cube_tex.set_magfilter(SamplerState.FT_linear_mipmap_linear )
        self.cube_tex.set_minfilter(SamplerState.FT_linear_mipmap_linear)

        self.common_inputs = {'render': render,
                              'camera': base.cam,
                              'depth_tex': self.depth,
                              'normal_tex': self.normal,
                              'albedo_tex': self.albedo,
                              'lit_tex': self.lit_tex,
                              'forward_tex': self.plain_tex,
                              'forward_aux_tex': self.plain_aux,
                              'cube_tex': self.cube_tex}

        self.filter_stages = filter_setup

        for stage in self.filter_stages:
            self.add_filter(**stage)
        for name, tex in self.filter_tex.items():
            self.common_inputs[name] = tex
        for filter_name, quad in self.filter_quad.items():
            quad.set_shader_inputs(**self.common_inputs)

        # stick the last stage quad to render2d
        # this is a bit ugly...
        if 'name' in self.filter_stages[-1]:
            last_stage = self.filter_stages[-1]['name']
        else:
            last_stage = self.filter_stages[-1]['shader']
        self.filter_quad[last_stage] = self.lightbuffer.get_texture_card()
        self.reload_filter(last_stage)
        self.filter_quad[last_stage].reparent_to(render2d)

        # listen to window events so that buffers can be resized with the
        # window
        self.accept("window-event", self._on_window_event)
        # update task
        taskMgr.add(self._update, '_update_tsk', sort=-150)

    def save_screenshot(self, name='screen', extension='png'):
        if 'name' in self.filter_stages[-1]:
            last_stage = self.filter_stages[-1]['name']
        else:
            last_stage = self.filter_stages[-1]['shader']
        tex=self.filter_tex[last_stage]
        base.graphicsEngine.extract_texture_data(tex, base.win.getGsg())
        #base.graphicsEngine.renderFrame()
        tex.write(name+'.'+extension)
        print('Screen saved to:', name+'.'+extension)

    def set_cubemap(self, cubemap):
        self.cube_tex=loader.load_cube_map(cubemap)
        tex_format=self.cube_tex.get_format()
        if tex_format == Texture.F_rgb:
            tex_format = Texture.F_srgb
        elif tex_format == Texture.F_rgba:
            tex_format = Texture.F_srgb_alpha
        self.cube_tex.set_format(tex_format)
        self.cube_tex.set_magfilter(SamplerState.FT_linear_mipmap_linear )
        self.cube_tex.set_minfilter(SamplerState.FT_linear_mipmap_linear)
        self.common_inputs['cube_tex']= self.cube_tex
        for quad in self.filter_quad.values():
            quad.set_shader_input('cube_tex', self.cube_tex)


    def set_material(self, node, roughness, metallic, glow, alpha=1.0):
        image = PNMImage(x_size=32, y_size=32, num_channels=4)
        image.fill(roughness, glow, metallic)
        image.alpha_fill(alpha)
        tex=Texture()
        tex.load(image)
        node.set_shader_input('tex_material',tex, 1)

    def set_near_far(self, near, far):
        base.cam.node().get_lens().set_near_far(near, far)
        lens = base.cam.node().get_lens()
        self.modelcam.node().set_lens(lens)
        self.lightcam.node().set_lens(lens)

    def reset_filters(self, filter_setup, shading_setup=None):
        """
        Remove all filters and creates a new filter list using the given filter_setup (dict)
        """
        # special case - get the inputs for the directionl light(s)
        dir_light_num_lights = self.get_filter_define(
            'final_light', 'NUM_LIGHTS')
        dir_light_color = self.get_filter_input('final_light', 'light_color')
        dir_light_dir = self.get_filter_input('final_light', 'direction')

        # remove buffers
        for buff in self.filter_buff.values():
            buff.clear_render_textures()
            base.win.get_gsg().get_engine().remove_window(buff)
        # remove quads, but keep the last one (detach it)
        # the last one should also be self.lightbuffer.get_texture_card()
        # so we don't need to keep a reference to it
        if 'name' in self.filter_stages[-1]:
            last_stage = self.filter_stages[-1]['name']
        else:
            last_stage = self.filter_stages[-1]['shader']
        for name, quad in self.filter_quad.items():
            if name != last_stage:
                quad.remove_node()
            else:
                quad.detach_node()
        for cam in self.filter_cam.values():
            cam.remove_node()
        # load the new values
        self.filter_buff = {}
        self.filter_quad = {}
        self.filter_tex = {}
        self.filter_cam = {}
        self.filter_stages = filter_setup
        for stage in self.filter_stages:
            self.add_filter(**stage)
        for name, tex in self.filter_tex.items():
            self.common_inputs[name] = tex
        for filter_name, quad in self.filter_quad.items():
            quad.set_shader_inputs(**self.common_inputs)
        # stick the last stage quad to render2d
        # this is a bit ugly...
        if 'name' in self.filter_stages[-1]:
            last_stage = self.filter_stages[-1]['name']
        else:
            last_stage = self.filter_stages[-1]['shader']
        self.filter_quad[last_stage] = self.lightbuffer.get_texture_card()
        self.reload_filter(last_stage)
        self.filter_quad[last_stage].reparent_to(render2d)

        # reapply the directional lights
        self.set_filter_define(
            'final_light', 'NUM_LIGHTS', dir_light_num_lights)
        if dir_light_color:
            self.set_filter_input('final_light', None, dir_light_color)
            self.set_filter_input('final_light', None, dir_light_dir)

        if shading_setup is None:
            shading_setup =self.shading_setup
        if shading_setup != self.shading_setup:
            self.light_root.set_shader(loader.load_shader_GLSL(
                self.v.format('point_light'), self.f.format('point_light'), shading_setup))
            self.geometry_root.set_shader(loader.load_shader_GLSL(
                self.v.format('geometry'), self.f.format('geometry'), shading_setup))
            self.plain_root.set_shader(loader.load_shader_GLSL(
                self.v.format('forward'), self.f.format('forward'), shading_setup))
            self.shading_setup=shading_setup

        size=1
        if 'FORWARD_SIZE' in self.shading_setup:
            size= self.shading_setup['FORWARD_SIZE']
        window_size = (base.win.get_x_size(), base.win.get_y_size())
        self.plain_buff.set_size(int(window_size[0]*size), int(window_size[1]*size))
        self.plain_root.set_shader_input('screen_size', Vec2(window_size[0]*size, window_size[1]*size))


    def reload_filter(self, stage_name):
        """
        Reloads the shader and inputs of a given filter stage
        """
        id = self._get_filter_stage_index(stage_name)
        shader = self.filter_stages[id]['shader']
        inputs = {}
        if 'inputs' in self.filter_stages[id]:
            inputs = self.filter_stages[id]['inputs']
        define = None
        if 'define' in self.filter_stages[id]:
            define = self.filter_stages[id]['define']
        self.filter_quad[stage_name].set_shader(loader.load_shader_GLSL(
            self.v.format(shader), self.f.format(shader), define))
        for name, value in inputs.items():
            if isinstance(value, str):
                value = loader.load_texture(value)
                inputs[name]=value
        inputs={**inputs, **self.common_inputs}
        self.filter_quad[stage_name].set_shader_inputs(**inputs)
        if 'translate_tex_name' in self.filter_stages[id]:
            for old_name, new_name in self.filter_stages[id]['translate_tex_name'].items():
                value = self.filter_tex[old_name]
                self.filter_quad[stage_name].set_shader_input(
                    str(new_name), value)

    def get_filter_define(self, stage_name, name):
        """
        Returns the current value of a shader pre-processor define for a given filter stage
        """
        if stage_name in self.filter_quad:
            id = self._get_filter_stage_index(stage_name)
            if 'define' in self.filter_stages[id]:
                if name in self.filter_stages[id]['define']:
                    return self.filter_stages[id]['define'][name]
        return None

    def set_filter_define(self, stage_name, name, value):
        """
        Sets a define value for the shader pre-processor for a given filter stage,
        The shader for that filter stage gets reloaded, so no need to call reload_filter()
        """
        if stage_name in self.filter_quad:
            id = self._get_filter_stage_index(stage_name)
            if 'define' in self.filter_stages[id]:
                if value is None:
                    if name in self.filter_stages[id]['define']:
                        del self.filter_stages[id]['define'][name]
                else:
                    self.filter_stages[id]['define'][name] = value
            elif value is not None:
                self.filter_stages[id]['define'] = {name: value}
            # reload the shader
            self.reload_filter(stage_name)

    def _get_filter_stage_index(self, name):
        """
        Returns the index of a filter stage
        """
        for index, stage in enumerate(self.filter_stages):
            if 'name' in stage:
                if stage['name'] == name:
                    return index
            elif stage['shader'] == name:
                return index
        raise IndexError('No stage named ' + name)

    def get_filter_input(self, stage_name, name):
        """
        Returns the shader input from a given stage
        """
        if stage_name in self.filter_quad:
            id = self._get_filter_stage_index(stage_name)
            return self.filter_quad[stage_name].get_shader_input(str(name))
        return None

    def set_filter_input(self, stage_name, name, value, modify_using=None):
        """
        Sets a shader input for a given filter stage.
        modify_using - should be an operator, like operator.add if you want to
                       change the value of an input based on the current value
        """
        if stage_name in self.filter_quad:
            id = self._get_filter_stage_index(stage_name)
            if name is None:
                self.filter_quad[stage_name].set_shader_input(value)
                return
            if modify_using is not None:
                value = modify_using(self.filter_stages[id][
                                     'inputs'][name], value)
                self.filter_stages[id]['inputs'][name] = value
            if isinstance(value, str):
                tex = loader.load_texture(value, sRgb='srgb'in value)
                if 'nearest' in value:
                    tex.set_magfilter(SamplerState.FT_nearest)
                    tex.set_minfilter(SamplerState.FT_nearest)
                if 'f_rgb16' in value:
                    tex.set_format(Texture.F_rgb16)
                if 'clamp' in value:
                    tex.set_wrap_u(Texture.WMClamp)
                    tex.set_wrap_v(Texture.WMClamp)
                value=tex
            self.filter_quad[stage_name].set_shader_input(str(name), value)
            # print(stage_name, name, value)

    def _setup_g_buffer(self, define=None):
        """
        Creates all the needed buffers, nodes and attributes for a geometry buffer
        """
        self.modelbuffer = self._make_FBO("model buffer", 1)
        self.lightbuffer = self._make_FBO("light buffer", 0)

        # Create four render textures: depth, normal, albedo, and final.
        # attach them to the various bitplanes of the offscreen buffers.
        self.depth = Texture()
        self.depth.set_wrap_u(Texture.WM_clamp)
        self.depth.set_wrap_v(Texture.WM_clamp)
        self.depth.set_format(Texture.F_depth_component32)
        self.depth.set_component_type(Texture.T_float)
        self.albedo = Texture()
        self.albedo.set_wrap_u(Texture.WM_clamp)
        self.albedo.set_wrap_v(Texture.WM_clamp)
        self.normal = Texture()
        self.normal.set_format(Texture.F_rgba16)
        self.normal.set_component_type(Texture.T_float)
        #self.normal.set_magfilter(SamplerState.FT_linear)
        #self.normal.set_minfilter(SamplerState.FT_linear_mipmap_linear)
        self.lit_tex = Texture()
        self.lit_tex.set_wrap_u(Texture.WM_clamp)
        self.lit_tex.set_wrap_v(Texture.WM_clamp)

        self.modelbuffer.add_render_texture(tex=self.depth,
                                          mode=GraphicsOutput.RTMBindOrCopy,
                                          bitplane=GraphicsOutput.RTPDepth)
        self.modelbuffer.add_render_texture(tex=self.albedo,
                                          mode=GraphicsOutput.RTMBindOrCopy,
                                          bitplane=GraphicsOutput.RTPColor)
        self.modelbuffer.add_render_texture(tex=self.normal,
                                          mode=GraphicsOutput.RTMBindOrCopy,
                                          bitplane=GraphicsOutput.RTP_aux_hrgba_0)
        self.lightbuffer.add_render_texture(tex=self.lit_tex,
                                          mode=GraphicsOutput.RTMBindOrCopy,
                                          bitplane=GraphicsOutput.RTPColor)
        # Set the near and far clipping planes.
        base.cam.node().get_lens().set_near_far(2.0, 70.0)
        lens = base.cam.node().get_lens()

        # This algorithm uses three cameras: one to render the models into the
        # model buffer, one to render the lights into the light buffer, and
        # one to render "plain" stuff (non-deferred shaded) stuff into the
        # light buffer.  Each camera has a bitmask to identify it.
        # self.modelMask = 1
        # self.lightMask = 2

        self.modelcam = base.make_camera(win=self.modelbuffer,
                                        lens=lens,
                                        scene=render,
                                        mask=BitMask32.bit(self.modelMask))
        self.lightcam = base.make_camera(win=self.lightbuffer,
                                        lens=lens,
                                        scene=render,
                                        mask=BitMask32.bit(self.lightMask))

        # Panda's main camera is not used.
        base.cam.node().set_active(0)

        # Take explicit control over the order in which the three
        # buffers are rendered.
        self.modelbuffer.set_sort(1)
        self.lightbuffer.set_sort(2)
        base.win.set_sort(3)

        # Within the light buffer, control the order of the two cams.
        self.lightcam.node().get_display_region(0).set_sort(1)

        # By default, panda usually clears the screen before every
        # camera and before every window.  Tell it not to do that.
        # Then, tell it specifically when to clear and what to clear.
        self.modelcam.node().get_display_region(0).disable_clears()
        self.lightcam.node().get_display_region(0).disable_clears()
        base.cam.node().get_display_region(0).disable_clears()
        base.cam2d.node().get_display_region(0).disable_clears()
        self.modelbuffer.disable_clears()
        base.win.disable_clears()

        self.modelbuffer.set_clear_color_active(1)
        self.modelbuffer.set_clear_depth_active(1)
        self.lightbuffer.set_clear_color_active(1)
        self.lightbuffer.set_clear_color((0, 0, 0, 0))
        self.modelbuffer.set_clear_color((0, 0, 0, 0))
        self.modelbuffer.set_clear_active(GraphicsOutput.RTP_aux_hrgba_0, True)

        render.set_state(RenderState.make_empty())

        # Create two subroots, to help speed cull traversal.
        # root node and a list for the lights
        self.light_root = render.attach_new_node('light_root')
        self.light_root.set_shader(loader.load_shader_GLSL(
            self.v.format('point_light'), self.f.format('point_light'), define))
        self.light_root.hide(BitMask32.bit(self.modelMask))
        self.light_root.set_shader_inputs(albedo_tex=self.albedo,
                                          depth_tex=self.depth,
                                          normal_tex=self.normal,
                                          camera=base.cam,
                                          render=render )
        # self.light_root.hide(BitMask32(self.plainMask))

        self.geometry_root = render.attach_new_node('geometry_root')
        self.geometry_root.set_shader(loader.load_shader_GLSL(
            self.v.format('geometry'), self.f.format('geometry'), define))
        self.geometry_root.hide(BitMask32.bit(self.lightMask))
        # self.geometry_root.hide(BitMask32(self.plainMask))

        self.plain_root, self.plain_tex, self.plain_cam, self.plain_buff, self.plain_aux = self._make_forward_stage(define)
        self.plain_root.set_shader(loader.load_shader_GLSL(
            self.v.format('forward'), self.f.format('forward'), define))
        self.plain_root.set_shader_input('depth_tex', self.depth)
        self.plain_root.set_shader_input('screen_size', Vec2(self.plain_tex.get_x_size(),self.plain_tex.get_y_size()))
        self.plain_root.set_shader_input('camera', self.plain_cam)
        mask=BitMask32.bit(self.modelMask)
        #mask.set_bit(self.lightMask)
        self.plain_root.hide(mask)

        #set aa
        #render.setAntialias(AntialiasAttrib.M_multisample)

        # instal into buildins
        builtins.deferred_render = self.geometry_root
        builtins.forward_render = self.plain_root

    def _on_window_event(self, window):
        """
        Function called when something hapens to the main window
        Currently it's only function is to resize all the buffers to fit
        the new size of the window if the size of the window changed
        """
        if window is not None:
            window_size = (base.win.get_x_size(), base.win.get_y_size())
            if self.last_window_size != window_size:
                lens = base.cam.node().get_lens()
                lens.set_aspect_ratio(float(window_size[0])/float(window_size[1]))
                self.modelcam.node().set_lens(lens)
                self.lightcam.node().set_lens(lens)
                self.plain_cam.node().set_lens(lens)

                self.modelbuffer.set_size(window_size[0], window_size[1])
                self.lightbuffer.set_size(window_size[0], window_size[1])
                #fix here!
                size=1
                if 'FORWARD_SIZE' in self.shading_setup:
                    size= self.shading_setup['FORWARD_SIZE']
                self.plain_buff.set_size(int(window_size[0]*size), int(window_size[1]*size))
                self.plain_root.set_shader_input('screen_size', Vec2(window_size[0]*size,window_size[1]*size))
                for buff in self.filter_buff.values():
                    old_size = buff.get_fb_size()
                    x_factor = float(old_size[0]) / \
                        float(self.last_window_size[0])
                    y_factor = float(old_size[1]) / \
                        float(self.last_window_size[1])
                    buff.set_size(
                        int(window_size[0] * x_factor), int(window_size[1] * y_factor))
                self.last_window_size = window_size

    def add_filter(self, shader, inputs={},
                   name=None, size=1.0,
                   clear_color=(0, 0, 0, 0), translate_tex_name=None,
                   define=None):
        """
        Creates and adds filter stage to the filter stage dicts:
        the created buffer is put in self.filter_buff[name]
        the created fullscreen quad is put in self.filter_quad[name]
        the created fullscreen texture is put in self.filter_tex[name]
        the created camera is put in self.filter_cam[name]
        """
        #print(inputs)
        if name is None:
            name = shader
        index = len(self.filter_buff)
        quad, tex, buff, cam = self._make_filter_stage(
            sort=index, size=size, clear_color=clear_color, name=name)
        self.filter_buff[name] = buff
        self.filter_quad[name] = quad
        self.filter_tex[name] = tex
        self.filter_cam[name] = cam

        quad.set_shader(loader.load_shader_GLSL(self.v.format(
            shader), self.f.format(shader), define))
        for name, value in inputs.items():
            if isinstance(value, str):
                value = loader.load_texture(value, sRgb=loader.use_srgb)
                inputs[name]=value
        quad.set_shader_inputs(**inputs)
        if translate_tex_name:
            for old_name, new_name in translate_tex_name.items():
                value = self.filter_tex[old_name]
                quad.set_shader_input(str(new_name), value)

    def _make_filter_stage(self, sort=0, size=1.0, clear_color=None, name=None):
        """
        Creates a buffer, quad, camera and texture needed for a filter stage
        Use add_filter() not this function
        """
        # make a root for the buffer
        root = NodePath("filterBufferRoot")
        tex = Texture()
        tex.set_wrap_u(Texture.WM_clamp)
        tex.set_wrap_v(Texture.WM_clamp)
        buff_size_x = int(base.win.get_x_size() * size)
        buff_size_y = int(base.win.get_y_size() * size)
        # buff=base.win.makeTextureBuffer("buff", buff_size_x, buff_size_y, tex)
        winprops = WindowProperties()
        winprops.set_size(buff_size_x, buff_size_y)
        props = FrameBufferProperties()
        props.set_rgb_color(True)
        props.set_rgba_bits(8, 8, 8, 8)
        props.set_depth_bits(0)
        buff = base.graphicsEngine.make_output(
            base.pipe, 'filter_stage_'+name, sort,
            props, winprops,
            GraphicsPipe.BF_resizeable,
            base.win.get_gsg(), base.win)
        buff.add_render_texture(
            tex=tex, mode=GraphicsOutput.RTMBindOrCopy, bitplane=GraphicsOutput.RTPColor)
        buff.set_sort(sort)
        #print(name, sort)
        # buff.setSort(0)
        if clear_color is None:
            buff.set_clear_active(GraphicsOutput.RTPColor, False)
        else:
            buff.set_clear_color(clear_color)
            buff.set_clear_active(GraphicsOutput.RTPColor, True)

        cam = base.make_camera(win=buff)
        cam.reparent_to(root)
        cam.set_pos(buff_size_x * 0.5, buff_size_y * 0.5, 100)
        cam.setP(-90)
        lens = OrthographicLens()
        lens.set_film_size(buff_size_x, buff_size_y)
        cam.node().set_lens(lens)
        # plane with the texture, a blank texture for now
        cm = CardMaker("plane")
        cm.setFrame(0, buff_size_x, 0, buff_size_y)
        quad = root.attach_new_node(cm.generate())
        quad.look_at(0, 0, -1)
        quad.set_light_off()
        '''Vertices=GeomVertexData('Triangle', GeomVertexFormat.getV3(), Geom.UHStatic)
        Vertex=GeomVertexWriter(Vertices, 'vertex')
        Vertex.addData3d(0.0,0.0,0.0)
        Vertex.addData3d(0.0,0.0,0.0)
        Vertex.addData3d(0.0,0.0,0.0)
        Triangle = GeomTriangles(Geom.UHStatic)
        Triangle.addVertices(0,1,2)
        Triangle.closePrimitive()
        Primitive=Geom(Vertices)
        Primitive.addPrimitive(Triangle)
        gNode=GeomNode('FullScreenTriangle')
        gNode.addGeom(Primitive)
        quad = NodePath(gNode)
        quad.reparent_to(root)'''

        return quad, tex, buff, cam

    def _make_forward_stage(self, define):
        """
        Creates nodes, buffers and whatnot needed for forward rendering
        """
        size=1
        if 'FORWARD_SIZE' in define:
            size= define['FORWARD_SIZE']

        root = NodePath("forwardRoot")
        tex = Texture()
        tex.set_wrap_u(Texture.WM_clamp)
        tex.set_wrap_v(Texture.WM_clamp)
        aux_tex = Texture()
        aux_tex.set_wrap_u(Texture.WM_clamp)
        aux_tex.set_wrap_v(Texture.WM_clamp)
        buff_size_x = int(base.win.get_x_size()*size)
        buff_size_y = int(base.win.get_y_size()*size)


        winprops = WindowProperties()
        winprops.set_size(buff_size_x, buff_size_y)
        props = FrameBufferProperties()
        props.set_rgb_color(True)
        props.set_rgba_bits(8, 8, 8, 8)
        props.set_srgb_color(False)
        if 'FORWARD_AUX' in define:
            props.set_aux_rgba(1)
        props.set_depth_bits(0)
        buff = base.graphicsEngine.make_output(
            base.pipe, 'forward_stage', 2,
            props, winprops,
            GraphicsPipe.BF_resizeable,
            base.win.get_gsg(), base.win)
        buff.add_render_texture(tex=tex, mode=GraphicsOutput.RTMBindOrCopy, bitplane=GraphicsOutput.RTPColor)
        if 'FORWARD_AUX' in define:
            buff.add_render_texture(tex=aux_tex,mode=GraphicsOutput.RTMBindOrCopy, bitplane=GraphicsOutput.RTPAuxRgba0)
            buff.set_clear_active(GraphicsOutput.RTPAuxRgba0, True)
        buff.set_clear_color((0, 0, 0, 0))
        cam = base.make_camera(win=buff)
        cam.reparent_to(root)
        lens = base.cam.node().get_lens()
        cam.node().set_lens(lens)
        mask = BitMask32.bit(self.modelMask)
        mask.set_bit(self.lightMask)
        cam.node().set_camera_mask(mask)
        return root, tex, cam, buff, aux_tex

    def set_directional_light(self, color, direction, shadow_size=0):
        """
        Sets value for a directional light,
        use the SceneLight class to set the lights!
        """
        self.filter_quad['final_light'].set_shader_inputs(light_color=color, direction=direction)

    def add_cone_light(self, color, pos=(0, 0, 0), hpr=(0, 0, 0),exponent=40,
                        radius=1.0, fov=45.0, shadow_size=0.0, bias=0.0005):
        """
        Creates a spotlight,
        use the ConeLight class, not this function!
        """
        if fov > 179.0:
            fov = 179.0
        xy_scale = math.tan(deg2Rad(fov * 0.5))
        model = loader.load_model("models/cone")
        model.reparent_to(self.light_root)
        model.set_scale(xy_scale, 1.0, xy_scale)
        model.flatten_strong()
        model.set_scale(radius)
        model.set_pos(pos)
        model.set_hpr(hpr)
        # debug=self.lights[-1].copyTo(self.plain_root)
        model.set_attrib(DepthTestAttrib.make(RenderAttrib.MLess))
        model.set_attrib(CullFaceAttrib.make(
            CullFaceAttrib.MCullCounterClockwise))
        model.set_attrib(ColorBlendAttrib.make(
            ColorBlendAttrib.MAdd, ColorBlendAttrib.OOne, ColorBlendAttrib.OOne))
        model.set_attrib(DepthWriteAttrib.make(DepthWriteAttrib.MOff))

        model.set_shader(loader.load_shader_GLSL(self.v.format(
            'spot_light'), self.f.format('spot_light'), self.shading_setup))
        model.set_shader_input("light_radius", float(radius))
        model.set_shader_input("light_pos", Vec4(pos, 1.0))
        model.set_shader_input("light_fov", deg2Rad(fov))
        p3d_light = render.attach_new_node(Spotlight("Spotlight"))
        p3d_light.set_pos(render, pos)
        p3d_light.setHpr(render, hpr)
        p3d_light.node().set_exponent(exponent)
        p3d_light.node().set_color(Vec4(color, 1.0))
        if shadow_size > 0.0:
            p3d_light.node().set_shadow_caster(True, shadow_size, shadow_size)
            model.set_shader_input("bias", bias)
            model.set_shader(loader.load_shader_GLSL(self.v.format(
            'spot_light_shadow'), self.f.format('spot_light_shadow'), self.shading_setup))
        # p3d_light.node().set_camera_mask(self.modelMask)
        model.set_shader_input("spot", p3d_light)
        #p3d_light.node().showFrustum()
        p3d_light.node().get_lens().set_fov(fov)
        p3d_light.node().get_lens().set_far(radius)
        p3d_light.node().get_lens().set_near(1.0)
        return model, p3d_light

    def add_point_light(self, color, model="models/sphere", pos=(0, 0, 0), radius=1.0, shadow_size=0):
        """
        Creates a omni (point) light,
        Use the SphereLight class to create lights!!!
        """
        #print('make light, shadow', shadow_size)
        # light geometry
        # if we got a NodePath we use it as the geom for the light
        if not isinstance(model, NodePath):
            model = loader.load_model(model)
        # self.lights.append(model)
        model.set_shader(loader.load_shader_GLSL(self.v.format(
            'point_light'), self.f.format('point_light'), self.shading_setup))
        model.set_attrib(DepthTestAttrib.make(RenderAttrib.MLess))
        model.set_attrib(CullFaceAttrib.make(
            CullFaceAttrib.MCullCounterClockwise))
        model.set_attrib(ColorBlendAttrib.make(
            ColorBlendAttrib.MAdd, ColorBlendAttrib.OOne, ColorBlendAttrib.OOne))
        model.set_attrib(DepthWriteAttrib.make(DepthWriteAttrib.MOff))

        p3d_light = render.attach_new_node(PointLight("PointLight"))
        p3d_light.set_pos(render, pos)

        if shadow_size > 0:
            model.set_shader(loader.load_shader_GLSL(self.v.format(
                'point_light_shadow'), self.f.format('point_light_shadow'), self.shading_setup))
            p3d_light.node().set_shadow_caster(True, shadow_size, shadow_size)
            p3d_light.node().set_camera_mask(BitMask32.bit(13))
            for i in range(6):
                p3d_light.node().get_lens(i).set_near_far(0.1, radius)
                p3d_light.node().get_lens(i).make_bounds()

        # shader inputs
        model.set_shader_inputs(light= Vec4(color, radius * radius),
                                shadowcaster= p3d_light,
                                near= 0.1,
                                bias= (1.0/radius)*0.095)

        model.reparent_to(self.light_root)
        model.set_pos(pos)
        model.set_scale(radius*1.1)
        return model, p3d_light

    def _make_FBO(self, name, auxrgba=0, multisample=0, srgb=False):
        """
        This routine creates an offscreen buffer.  All the complicated
        parameters are basically demanding capabilities from the offscreen
        buffer - we demand that it be able to render to texture on every
        bitplane, that it can support aux bitplanes, that it track
        the size of the host window, that it can render to texture
        cumulatively, and so forth.
        """
        winprops = WindowProperties()
        props = FrameBufferProperties()
        props.set_rgb_color(True)
        props.set_rgba_bits(8,8,8,8)
        props.set_depth_bits(32)
        props.set_aux_hrgba(auxrgba)
        #props.set_aux_rgba(auxrgba)
        props.set_srgb_color(srgb)
        if multisample>0:
            props.set_multisamples(multisample)
        return base.graphicsEngine.make_output(
            base.pipe, name, 2,
            props, winprops,
            GraphicsPipe.BFSizeTrackHost | GraphicsPipe.BFCanBindEvery |
            GraphicsPipe.BFRttCumulative | GraphicsPipe.BFRefuseWindow,
            base.win.get_gsg(), base.win)

    def _update(self, task):
        """
        Update task, updates the forward rendering camera pos/hpr and attached lights
        """
        self.plain_cam.set_pos_hpr(base.cam.get_pos(render), base.cam.get_hpr(render))
        to_del=[]
        for id, (node, light, offset) in self.attached_lights.items():
            if not node.is_empty():
                light.set_pos(render.get_relative_point(node, offset))
            else:
                to_del.append(id)
        for id in to_del:
            self.attached_lights[id][1].remove()
        return task.again

# this will replace the default Loader
#Here Be CamelCase, Argh!

class WrappedLoader(object):

    def __init__(self, original_loader):
        self.original_loader = original_loader
        self.texture_shader_inputs = []
        self.use_srgb = ConfigVariableBool('framebuffer-srgb').getValue()
        self.shader_cache = {}

    def _from_snake_case(self, attr):
        camel_case=''
        up=False
        for char in attr:
            if up:
                char=char.upper()
            if char == "_":
                up=True
            else:
                up=False
                camel_case+=char
        return camel_case

    @lru_cache(maxsize=64)
    def __getattr__(self,attr):
        new_attr=self._from_snake_case(attr)
        if hasattr(self, new_attr):
            return self.__getattribute__(new_attr)

    def fix_transparency(self, model):
        for tex_stage in model.find_all_texture_stages():
            tex = model.find_texture(tex_stage)
            if tex:
                mode = tex_stage.get_mode()
                tex_format = tex.get_format()
                if mode == TextureStage.M_modulate and (tex_format == Texture.F_rgba or tex_format == Texture.F_srgb_alpha):
                    return
        model.set_transparency(TransparencyAttrib.MNone, 1)
        #model.clear_transparency()

    def fixSrgbTextures(self, model):
        for tex_stage in model.find_all_texture_stages():
            tex = model.find_texture(tex_stage)
            if tex:
                file_name = tex.get_filename()
                tex_format = tex.get_format()
                # print( tex_stage,  file_name, tex_format)
                if tex_stage.get_mode() == TextureStage.M_normal:
                    tex_stage.set_mode(TextureStage.M_normal_gloss)
                if tex_stage.get_mode() != TextureStage.M_normal_gloss:
                    if tex_format == Texture.F_rgb:
                        tex_format = Texture.F_srgb
                    elif tex_format == Texture.F_rgba:
                        tex_format = Texture.F_srgb_alpha
                tex.set_format(tex_format)
                model.set_texture(tex_stage, tex, 1)

    def setTextureInputs(self, node):
        for child in node.get_children():
            #print(child)
            self._setTextureInputs(child)
            self.setTextureInputs(child)


    def _setTextureInputs(self, model):
        #print ('Fixing model', model)
        slots_filled = set()
        # find all the textures, easy mode - slot is fitting the stage mode
        # (eg. slot0 is diffuse/color)
        for slot, tex_stage in enumerate(model.findAllTextureStages()):
            if slot >= len(self.texture_shader_inputs):
                break
            tex = model.find_texture(tex_stage)
            if tex:
                #print('Found tex:', tex.getFilename())
                mode = tex_stage.getMode()
                if mode in self.texture_shader_inputs[slot]['stage_modes']:
                    model.set_shader_input(self.texture_shader_inputs[
                                         slot]['input_name'], tex)
                    slots_filled.add(slot)
        # did we get all of them?
        if len(slots_filled) == len(self.texture_shader_inputs):
            return
        # what slots need filling?
        missing_slots = set(
            range(len(self.texture_shader_inputs))) - slots_filled
        for slot, tex_stage in enumerate(model.findAllTextureStages()):
            if slot >= len(self.texture_shader_inputs):
                break
            if slot in missing_slots:
                tex = model.find_texture(tex_stage)
                if tex:
                    mode = tex_stage.get_mode()
                    for d in self.texture_shader_inputs:
                        if mode in d['stage_modes']:
                            i = self.texture_shader_inputs.index(d)
                            model.set_shader_input(self.texture_shader_inputs[
                                                 i]['input_name'], tex)
                            slots_filled.add(i)
        # did we get all of them this time?
        if len(slots_filled) == len(self.texture_shader_inputs):
            return
        missing_slots = set(
            range(len(self.texture_shader_inputs))) - slots_filled
        #print ('Fail for model:', model)
        # set defaults
        for slot in missing_slots:
            model.set_shader_input(self.texture_shader_inputs[slot][
                                 'input_name'], self.texture_shader_inputs[slot]['default_texture'])

    def destroy(self):
        self.original_loader.destroy()

    def loadModel(self, modelPath, loaderOptions=None, noCache=None,
                  allowInstance=False, okMissing=None,
                  callback=None, extraArgs=[], priority=None):
        model = self.original_loader.loadModel(
            modelPath, loaderOptions, noCache, allowInstance, okMissing, callback, extraArgs, priority)

        if self.use_srgb:
            self.fixSrgbTextures(model)
        self.setTextureInputs(model)
        self.fix_transparency(model)
        return model

    def cancelRequest(self, cb):
        self.original_loader.cancelRequest(cb)

    def isRequestPending(self, cb):
        return self.original_loader.isRequestPending(cb)

    def loadModelOnce(self, modelPath):
        return self.original_loader.loadModelOnce(modelPath)

    def loadModelCopy(self, modelPath, loaderOptions=None):
        return self.original_loader.loadModelCopy(modelPath, loaderOptions)

    def loadModelNode(self, modelPath):
        return self.original_loader.loadModelNode(modelPath)

    def unloadModel(self, model):
        self.original_loader.unloadModel(model)

    def saveModel(self, modelPath, node, loaderOptions=None,
                  callback=None, extraArgs=[], priority=None):
        return self.original_loader.saveModel(modelPath, node, loaderOptions, callback, extraArgs, priority)

    def loadFont(self, modelPath,
                 spaceAdvance=None, lineHeight=None,
                 pointSize=None,
                 pixelsPerUnit=None, scaleFactor=None,
                 textureMargin=None, polyMargin=None,
                 minFilter=None, magFilter=None,
                 anisotropicDegree=None,
                 color=None,
                 outlineWidth=None,
                 outlineFeather=0.1,
                 outlineColor=VBase4(0, 0, 0, 1),
                 renderMode=None,
                 okMissing=False):
        return self.original_loader.loadFont(modelPath, spaceAdvance, lineHeight, pointSize, pixelsPerUnit, scaleFactor, textureMargin, polyMargin, minFilter, magFilter, anisotropicDegree, color, outlineWidth, outlineFeather, outlineColor, renderMode, okMissing)

    def loadTexture(self, texturePath, alphaPath=None,
                    readMipmaps=False, okMissing=False,
                    minfilter=None, magfilter=None,
                    anisotropicDegree=None, loaderOptions=None,
                    multiview=None, sRgb=False):
        tex = self.original_loader.loadTexture(
            texturePath, alphaPath, readMipmaps, okMissing, minfilter, magfilter, anisotropicDegree, loaderOptions, multiview)
        if sRgb:
            tex_format = tex.getFormat()
            if tex_format == Texture.F_rgb:
                tex_format = Texture.F_srgb
            elif tex_format == Texture.F_rgba:
                tex_format = Texture.F_srgb_alpha
            tex.setFormat(tex_format)
        return tex

    def load3DTexture(self, texturePattern, readMipmaps=False, okMissing=False,
                      minfilter=None, magfilter=None, anisotropicDegree=None,
                      loaderOptions=None, multiview=None, numViews=2):
        return self.original_loader.load3DTexture(texturePattern, readMipmaps, okMissing, minfilter, magfilter, anisotropicDegree, loaderOptions, multiview, numViews)

    def load2DTextureArray(self, texturePattern, readMipmaps=False, okMissing=False,
                           minfilter=None, magfilter=None, anisotropicDegree=None,
                           loaderOptions=None, multiview=None, numViews=2):
        return self.original_loader.load2DTextureArray(texturePattern, readMipmaps, okMissing, minfilter, magfilter, anisotropicDegree, loaderOptions, multiview, numViews)

    def loadCubeMap(self, texturePattern, readMipmaps=False, okMissing=False,
                    minfilter=None, magfilter=None, anisotropicDegree=None,
                    loaderOptions=None, multiview=None):
        return self.original_loader.loadCubeMap(texturePattern, readMipmaps, okMissing, minfilter, magfilter, anisotropicDegree, loaderOptions, multiview)

    def unloadTexture(self, texture):
        self.original_loader.unloadTexture(texture)

    def loadSfx(self, *args, **kw):
        return self.original_loader.loadSfx(*args, **kw)

    def loadMusic(self, *args, **kw):
        return self.original_loader.loadMusic(*args, **kw)

    def loadSound(self, manager, soundPath, positional=False,
                  callback=None, extraArgs=[]):
        return self.original_loader.loadSound(manager, soundPath, positional, callback, extraArgs)

    def unloadSfx(self, sfx):
        self.original_loader.unloadSfx(sfx)

    def loadShaderGLSL(self, v_shader, f_shader, define=None, version='#version 130'):
        # check if we already have a shader like that
        # note: this may fail depending on the dict implementation
        if (v_shader, f_shader, str(define)) in self.shader_cache:
            return self.shader_cache[(v_shader, f_shader, str(define))]
        # load the shader text
        with open(getModelPath().findFile(v_shader).toOsSpecific()) as f:
            v_shader_txt = f.read()
        with open(getModelPath().findFile(f_shader).toOsSpecific()) as f:
            f_shader_txt = f.read()
        # make the header
        if define:
            header = version + '\n'
            for name, value in define.items():
                header += '#define {0} {1}\n'.format(name, value)
            # put the header on top
            v_shader_txt = v_shader_txt.replace(version, header)
            f_shader_txt = f_shader_txt.replace(version, header)
        # make the shader
        shader = Shader.make(Shader.SL_GLSL, v_shader_txt, f_shader_txt)
        # store it
        self.shader_cache[(v_shader, f_shader, str(define))] = shader
        try:
            shader.set_filename(Shader.ST_vertex, v_shader)
            shader.set_filename(Shader.ST_fragment, f_shader)
        except:
            print('Shader filenames will not be available, consider using a dev version of Panda3D')
        return shader

    def loadShader(self, shaderPath, okMissing=False):
        return self.original_loader.loadShader(shaderPath, okMissing)

    def unloadShader(self, shaderPath):
        self.original_loader.unloadShader(shaderPath)

    def asyncFlattenStrong(self, model, inPlace=True,
                           callback=None, extraArgs=[]):
        self.original_loader.asyncFlattenStrong(
            model, inPlace, callback, extraArgs)

# light classes:
class SceneLight(object):
    """
    Directional light(s) for the deferred renderer
    Because of the way directional lights are implemented (fullscreen quad),
    it's not very logical to have multiple SceneLights, but you can have multiple
    directional lights as part of one SceneLight instance.
    You can add and remove additional lights using add_light() and remove_light()
    This class curently has no properies access :(
    """

    def __init__(self, color=None, direction=None, main_light_name='main', shadow_size=0):
        if not hasattr(builtins, 'deferred_renderer'):
            raise RuntimeError('You need a DeferredRenderer')
        self.__color = {}
        self.__direction = {}
        self.__shadow_size = {}
        self.main_light_name = main_light_name
        if color and direction:
            self.add_light(color=color, direction=direction,
                           name=main_light_name, shadow_size=shadow_size)

    def add_light(self, color, direction, name, shadow_size=0):
        """
        Adds a directional light to this SceneLight
        """
        if len(self.__color) == 0:
            deferred_renderer.set_directional_light(
                color, direction, shadow_size)
            self.__color[name] = Vec3(color)
            self.__direction[name] = Vec3(*direction)
            self.__shadow_size[name] = shadow_size
        else:
            self.__color[name] = Vec3(color)
            self.__direction[name] = Vec3(direction)
            self.__shadow_size[name] = shadow_size
            num_lights = len(self.__color)
            colors = PTALVecBase3f()
            for v in self.__color.values():
                colors.push_back(v)
            directions = PTALVecBase3f()
            for v in self.__direction.values():
                directions.push_back(v)
            deferred_renderer.set_filter_define(
                'final_light', 'NUM_LIGHTS', num_lights)
            deferred_renderer.set_filter_input(
                'final_light', 'light_color', colors)
            deferred_renderer.set_filter_input(
                'final_light', 'direction', directions)

    def remove_light(self, name=None):
        """
        Removes a light from this SceneLight,
        if name is None, the 'main' light (created at init) is removed
        """
        if name is None:
            name = self.main_light_name
        if name in self.__color:
            del self.__color[name]
            del self.__direction[name]
            del self.__shadow_size[name]
            if len(self.__color) == 0:
                deferred_renderer.set_directional_light(
                    (0, 0, 0), (0, 0, 0), 0)
            elif len(self.__color) == 1:
                deferred_renderer.set_filter_define(
                    'final_light', 'NUM_LIGHTS', None)
                last_name = self.__color.keys()[0]
                deferred_renderer.set_directional_light(self.__color[last_name], self.__direction[
                    last_name], self.__shadow_size[last_name])
            else:
                num_lights = len(self.__color)
                colors = PTALVecBase3f()
                for v in self.__color.values():
                    colors.push_back(v)
                directions = PTALVecBase3f()
                for v in self.__direction.values():
                    directions.push_back(v)
                deferred_renderer.set_filter_define(
                    'final_light', 'NUM_LIGHTS', num_lights)
                deferred_renderer.set_filter_input(
                    'final_light', 'light_color', colors)
                deferred_renderer.set_filter_input(
                    'final_light', 'direction', directions)
            return True
        return False

    def set_color(self, color, name=None):
        """
        Sets light color
        """
        if name is None:
            name = self.main_light_name
        self.__color[name] = color
        if len(self.__color) == 1:
            deferred_renderer.set_directional_light(
                color, self.__direction[name], self.__shadow_size[name])
        else:
            colors = PTALVecBase3f()
            for v in self.__color.values():
                colors.push_back(v)
            deferred_renderer.set_filter_input(
                    'final_light', 'light_color', colors)

    def set_direction(self, direction, name=None):
        """
        Sets light direction
        """
        if name is None:
            name = self.main_light_name
        self.__direction[name] = direction
        if len(self.__color) == 1:
            deferred_renderer.set_directional_light(
                self.__color[name], direction, self.__shadow_size[name])
        else:
            directions = PTALVecBase3f()
            for v in self.__direction.values():
                directions.push_back(v)
            deferred_renderer.set_filter_input(
                    'final_light', 'direction', directions)

    def remove(self):
        deferred_renderer.set_filter_define('final_light', 'NUM_LIGHTS', None)
        deferred_renderer.set_directional_light((0, 0, 0), (0, 0, 0), 0)

    def __del__(self):
        try:
            self.remove()
        except:
            pass


class SphereLight(object):
    """
    Point (omni) light for the deferred renderer.
    Create a new SphereLight for each light you want to use,
    remember to keep a reference to the light instance
    the light will be removed by the garbage collector when it goes out of scope

    It is recomended to use properties to configure the light after creation eg.
    l=SphereLight(...)
    l.pos=Point3(...)
    l.color=(r,g,b)
    l.radius= 13
    """

    def __init__(self, color, pos, radius, shadow_size=None, shadow_bias=None):
        if not hasattr(builtins, 'deferred_renderer'):
            raise RuntimeError('You need a DeferredRenderer')
        self.__radius = radius
        self.__color = color
        self.light_id=None
        if shadow_size is None:
            shadow_size=deferred_renderer.shadow_size
        self.geom, self.p3d_light = deferred_renderer.add_point_light(color=color,
                                                                      model="models/sphere",
                                                                      pos=pos,
                                                                      radius=radius,
                                                                      shadow_size=shadow_size)
        self.set_shadow_bias(shadow_bias)

    def attach_to(self, node, offset=(0,0,0)):
        self.light_id=len(deferred_renderer.attached_lights)
        deferred_renderer.attached_lights[self.light_id]=(node, self, Point3(*offset))

    def detach(self):
        if self.light_id:
            del deferred_renderer.attached_lights[self.light_id]

    def set_shadow_size(self, size):
        if size >0:
            self.p3d_light.node().set_shadow_caster(True, size, size)
            self.p3d_light.node().set_camera_mask(BitMask32.bit(13))
            for i in range(6):
                self.p3d_light.node().get_lens(i).set_near_far(0.1, self.__radius)
                self.p3d_light.node().get_lens(i).make_bounds()

            shader=loader.load_shader_GLSL(deferred_renderer.v.format('point_light_shadow'),
                                           deferred_renderer.f.format('point_light_shadow'),
                                           deferred_renderer.shading_setup)
            self.geom.set_shader_input('shadowcaster', self.p3d_light)
            self.set_shadow_bias(self.shadow_bias)
            self.geom.set_shader(shader)
        else:
            self.p3d_light.node().set_shadow_caster(False)
            shader=loader.load_shader_GLSL(deferred_renderer.v.format('point_light'),
                                           deferred_renderer.f.format('point_light'),
                                           deferred_renderer.shading_setup)
            self.geom.set_shader(shader)
            try:
                buff = self.p3d_light.node().get_shadow_buffer(base.win.get_gsg())
                buff.clear_render_textures()
                base.win.get_gsg().get_engine().remove_window(buff)
            except:
                pass

    def set_shadow_bias(self, bias):
        self.shadow_bias=bias
        if bias is not None:
            self.geom.set_shader_input("bias", bias)


    def set_color(self, color):
        """
        Sets light color
        """
        self.geom.set_shader_input("light", Vec4(
            color, self.__radius * self.__radius))
        self.__color = color

    def set_radius(self, radius):
        """
        Sets light radius
        """
        self.geom.set_shader_input("light", Vec4(self.__color, radius * radius))
        self.geom.set_scale(radius)
        self.__radius = radius
        try:
            for i in range(6):
                self.p3d_light.node().get_lens(i).set_near_far(0.1, radius)
        except:
            pass

    def set_pos(self, *args):
        """
        Sets light position,
        you can pass in a NodePath as the first argument to make the pos relative to that node
        """
        if self.geom.is_empty():
            return
        if len(args) < 1:
            return
        elif len(args) == 1:  # one arg, must be a vector
            pos = Vec3(args[0])
        elif len(args) == 2:  # two args, must be a node and  vector
            pos = render.get_relative_point(args[0], Vec3(args[1]))
        elif len(args) == 3:  # vector
            pos = Vec3(args[0], args[1], args[2])
        elif len(args) == 4:  # node and vector?
            pos = render.get_relative_point(
                args[0], Vec3(args[0], args[1], args[2]))
        else:  # something ???
            pos = Vec3(args[0], args[1], args[2])
        #self.geom.setShaderInput("light_pos", Vec4(pos, 1.0))
        self.geom.set_pos(render, pos)
        self.p3d_light.set_pos(render, pos)

    def remove(self):
        self.geom.remove_node()
        try:
            buff = self.p3d_light.node().get_shadow_buffer(base.win.get_gsg())
            buff.clear_render_textures()
            base.win.get_gsg().get_engine().remove_window(buff)
            self.p3d_light.node().set_shadow_caster(False)
        except:
            pass
        if self.light_id and self.light_id in deferred_renderer.attached_lights:
            del deferred_renderer.attached_lights[self.light_id]
        self.p3d_light.remove_node()

    def __del__(self):
        try:
            if not self.geom.is_empty():
                self.remove()
        except:
            pass

    @property
    def pos(self):
        return self.geom.get_pos(render)

    @pos.setter
    def pos(self, p):
        self.set_pos(p)

    @property
    def color(self):
        return self.__color

    @color.setter
    def color(self, c):
        self.set_color(c)

    @property
    def radius(self):
        return self.__radius

    @radius.setter
    def radius(self, r):
        self.set_radius(float(r))


class ConeLight(object):
    """
    Spot light for the deferred renderer.
    Create a new ConeLight for each light you want to use,
    remember to keep a reference to the light instance
    the light will be removed by the garbage collector when it goes out of scope

    You can set the hpr of the light by passing a node or position as the look_at argument

    It is recomended to use properties to configure the light after creation eg.
    l=ConeLight(...)
    l.pos=Point3(...)
    l.color=(r,g,b)
    l.radius= 13
    l.fov=45.0
    l.hpr=Point3(...)
    the lookAt() function can also be used to set a hpr in a different way
    """

    def __init__(self, color, pos, radius, fov, hpr=None,
                look_at=None, exponent=40, shadow_size=0, bias=0.0005):
        if not hasattr(builtins, 'deferred_renderer'):
            raise RuntimeError('You need a DeferredRenderer')
        self.__radius = radius
        self.__color = color
        self.__pos = pos
        self.__hpr = hpr
        self.__fov = fov
        self.__shadow_size = shadow_size
        self.__shadow_bias=bias
        if hpr is None:
            dummy = render.attach_new_node('dummy')
            dummy.set_pos(pos)
            dummy.look_at(look_at)
            hpr = dummy.get_hpr(render)
            dummy.remove_node()
        self.__hpr = hpr
        self.geom, self.p3d_light = deferred_renderer.add_cone_light(color=color,
                                                                     pos=pos,
                                                                     hpr=hpr,
                                                                     exponent=exponent,
                                                                     radius=radius,
                                                                     fov=fov,
                                                                     shadow_size=shadow_size,
                                                                     bias=bias)
    def set_exponent(self, exponent):
        self.p3d_light.node().set_exponent(exponent)

    def set_fov(self, fov):
        """
        Sets the Field of View (in degrees) of the light
        Angles above 120 deg are not recomended,
        Angles above 179 deg are not supported
        """
        if fov > 179.0:
            fov = 179.0
        self.p3d_light.node().get_lens().set_fov(fov)
        # we might as well start from square 1...
        self.geom.remove_node()
        xy_scale = math.tan(deg2Rad(fov * 0.5))
        self.geom = loader.load_model("models/cone")
        self.geom.reparent_to(deferred_renderer.light_root)
        self.geom.set_scale(xy_scale, 1.0, xy_scale)
        self.geom.flatten_strong()
        self.geom.set_scale(self.__radius)
        self.geom.set_pos(self.__pos)
        self.geom.set_hpr(self.__hpr)
        self.geom.set_attrib(DepthTestAttrib.make(RenderAttrib.MLess))
        self.geom.set_attrib(CullFaceAttrib.make(
            set_attrib.MCullCounterClockwise))
        self.geom.setAttrib(ColorBlendAttrib.make(
            set_attrib.MAdd, ColorBlendAttrib.OOne, ColorBlendAttrib.OOne))
        self.geom.set_attrib(DepthWriteAttrib.make(DepthWriteAttrib.MOff))
        self.geom.set_shader(loader.loadShaderGLSL(deferred_renderer.v.format(
            'spot_light'), deferred_renderer.f.format('spot_light'), deferred_renderer.shading_setup))
        self.geom.set_shader_inputs(light_radius= float(self.__radius),
                                    light_pos= Vec4(self.__pos, 1.0),
                                    light_fov= deg2Rad(fov),
                                    spot= self.p3d_light)
        self.__fov = fov

    def set_radius(self, radius):
        """
        Sets the radius (range) of the light
        """
        self.geom.set_shader_input("light_radius", float(radius))
        self.geom.set_scale(radius)
        self.__radius = radius
        try:
            self.p3d_light.node().get_lens().set_near_far(0.1, radius)
        except:
            pass

    def setHpr(self, hpr):
        """
        Sets the HPR of a light
        """
        self.geom.set_hpr(hpr)
        self.p3d_light.set_hpr(hpr)
        self.__hpr = hrp

    def set_pos(self, *args):
        """
        Sets light position,
        you can pass in a NodePath as the first argument to make the pos relative to that node
        """
        if len(args) < 1:
            return
        elif len(args) == 1:  # one arg, must be a vector
            pos = Vec3(args[0])
        elif len(args) == 2:  # two args, must be a node and  vector
            pos = render.get_relative_point(args[0], Vec3(args[1]))
        elif len(args) == 3:  # vector
            pos = Vec3(args[0], args[1], args[2])
        elif len(args) == 4:  # node and vector?
            pos = render.get_relative_point(
                args[0], Vec3(args[0], args[1], args[2]))
        else:  # something ???
            pos = Vec3(args[0], args[1], args[2])
        self.geom.set_pos(pos)
        self.p3d_light.set_pos(pos)
        self.__pos = pos

    def lookAt(self, node_or_pos):
        """
        Sets the hpr of the light so that it looks at the given node or pos
        """
        self.look_at(node_or_pos)

    def look_at(self, node_or_pos):
        """
        Sets the hpr of the light so that it looks at the given node or pos
        """
        self.geom.look_at(node_or_pos)
        self.p3d_light.look_at(node_or_pos)
        self.__hpr = self.p3d_light.get_hpr(render)

    def set_shadow_bias(self, bias):
        self.__shadow_bias=bias
        if bias is not None:
            self.geom.set_shader_input("bias", bias)

    def remove(self):
        self.geom.removeNode()
        try:
            buff = self.p3d_light.node().get_shadow_buffer(base.win.get_gsg())
            buff.clear_render_textures()
            base.win.get_gsg().get_engine().remove_window(buff)
            self.p3d_light.node().set_shadow_caster(False)
        except:
            pass
        self.p3d_light.remove_node()

    def __del__(self):
        try:
            self.remove()
        except:
            pass

    @property
    def fov(self):
        return self.__fov

    @fov.setter
    def fov(self, f):
        self.set_fov(f)

    @property
    def hpr(self):
        return self.geom.get_hpr(render)

    @hpr.setter
    def hpr(self, p):
        self.setHpr(p)

    @property
    def pos(self):
        return self.geom.get_pos(render)

    @pos.setter
    def pos(self, p):
        self.set_pos(p)

    @property
    def color(self):
        return self.__color

    @color.setter
    def color(self, c):
        self.set_color(c)

    @property
    def radius(self):
        return self.__radius

    @radius.setter
    def radius(self, r):
        self.set_radius(float(r))
