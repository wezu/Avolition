'''Avolition 2.0
INFO:
    This module handles loading, parsing and saving .ini configuration,
    and also changing graphic options and key binds live
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
import configparser
from copy import copy
from panda3d.core import *
from direct.showbase.DirectObject import DirectObject


class Options(DirectObject):
    def __init__(self):
        pass

    def update_options_highlight(self):
        d={
            'bloom_button':self._find_stage('base_bloom'),
            'ao_button':self._find_stage('ao'),
            'lut_button' : not deferred_renderer.get_filter_define('pre_aa', 'DISABLE_LUT'),
            'ssr_button':self._find_stage('base_ssr'),
            'dof_button' : self._find_stage('fog'),
            'chroma_button':self._find_stage('chroma'),
            'hi_shadow_button':deferred_renderer.shadow_size >= 1024,
            'med_shadow_button':deferred_renderer.shadow_size == 512,
            'lo_shadow_button':deferred_renderer.shadow_size == 256,
            'no_shadow_button':deferred_renderer.shadow_size == 0,
            'button_preset_full': Config.get('graphics','preset')=='full',
            'button_preset_medium':Config.get('graphics','preset')=='medium',
            'button_preset_minimal':Config.get('graphics','preset')=='minimal',
            }
        for k,v in d.items():
            if v:
                game.gui.highlight(on=True, name=k)
            else:
                game.gui.highlight(on=False, name=k)


    def set_bloom(self):
        stage_index=self._find_stage('base_bloom')
        new_preset=copy(deferred_renderer.filter_stages)
        if stage_index is None:
            bloom_stage={'name':'base_bloom',
                        'shader' : 'bloom',
                        'size': 0.5,
                        'inputs':{'power' : 2.0,
                                 'desat' : 0.5,
                                 'scale' : 10.0}
                        }
            blur_stage={'name': 'bloom',
                        'translate_tex_name': {'base_bloom': 'input_tex'},
                        'shader': 'blur',
                        'inputs': {'blur': 3.0},
                        'size': 0.5}
            self._set_filter(filter_dict=bloom_stage, define=(('mix', 'DISABLE_BLOOM', None),), stages=new_preset)
            self._set_filter(filter_dict=blur_stage, stage=2, stages=new_preset)
        else:
            self._set_filter(filter_dict=None, define=(('mix', 'DISABLE_BLOOM', 1),), stage=stage_index, stages=new_preset)
            stage_index=self._find_stage('bloom', stages=new_preset )
            if stage_index:
                self._set_filter(filter_dict=None, stage=stage_index, stages=new_preset)
        #tell the renderer something changed
        deferred_renderer.reset_filters(new_preset)
        #write the new config
        self.write_graphics_config(new_preset, deferred_renderer.shadow_size, deferred_renderer.shading_setup, 'data/user/presets/custom.ini')
        Config.set('graphics','preset', 'custom')
        self.update_options_highlight()

    def set_ssr(self):
        stage_index=self._find_stage('base_ssr')
        new_preset=copy(deferred_renderer.filter_stages)
        if stage_index is None:
            ssr_stage={'name': 'base_ssr',
                       'define' :{ 'maxDelta' : 0.044,
                                   'rayLength' : 0.034,
                                   'stepsCount': 16,
                                    'fade' : 0.3},
                        'shader': 'ssr',
                        'size' : 0.5}
            blur_stage={'name':'ssr',
                        'shader': 'ref_blur',
                        'inputs': {'blur' : 6.0,
                                 'noise_tex' : 'tex/noise.png'},
                        'size': 0.5}
            self._set_filter(filter_dict=ssr_stage, define=(('mix', 'DISABLE_SSR', None),), stages=new_preset)
            self._set_filter(filter_dict=blur_stage, stage=2, stages=new_preset)
        else:
            self._set_filter(filter_dict=None, define=(('mix', 'DISABLE_SSR', 1),), stage=stage_index, stages=new_preset)
            stage_index=self._find_stage('ssr', stages=new_preset )
            if stage_index:
                self._set_filter(filter_dict=None, stage=stage_index, stages=new_preset)
        #tell the renderer something changed
        deferred_renderer.reset_filters(new_preset)
        #write the new config
        self.write_graphics_config(new_preset, deferred_renderer.shadow_size, deferred_renderer.shading_setup, 'data/user/presets/custom.ini')
        Config.set('graphics','preset', 'custom')
        self.update_options_highlight()


    def set_lut(self):
        new_preset=copy(deferred_renderer.filter_stages)
        if deferred_renderer.get_filter_define('pre_aa', 'DISABLE_LUT') is None:
            self._set_define('pre_aa', 'DISABLE_LUT', 1, new_preset)
        else:
            self._set_define('pre_aa', 'DISABLE_LUT', None, new_preset)
        #tell the renderer something changed
        deferred_renderer.reset_filters(new_preset)
        #write the new config
        self.write_graphics_config(new_preset, deferred_renderer.shadow_size, deferred_renderer.shading_setup, 'data/user/presets/custom.ini')
        Config.set('graphics','preset', 'custom')
        self.update_options_highlight()

    def set_dof_fog(self):
        stage_index=self._find_stage('fog')
        new_preset=copy(deferred_renderer.filter_stages)
        if stage_index is None:
            fog_stage={'shader':'fog',
                       'translate_tex_name':{'mix': 'input_tex'},
                        'inputs':{'fog_start' : 20.0,
                                 'fog_max' : 40.0,
                                 'dof_near' : 3.0,
                                 'dof_far_start' : 10.0,
                                 'dof_far_max' : 35.0,
                                 'fog_color' : Vec3(0.0, 0.0, 0.0)}}
            dof_stage={'shader':'dof',
                        'translate_tex_name':{'fog':'input_tex'},
                        'inputs' : {'blur' : 15.0}}
            mix_stage_index=self._find_stage('mix', stages=new_preset )
            self._set_filter(filter_dict=fog_stage, stage=mix_stage_index+1, stages=new_preset)
            self._set_filter(filter_dict=dof_stage, stage=mix_stage_index+2, stages=new_preset)
        else:
            self._set_filter(filter_dict=None, stage=stage_index, stages=new_preset)
            stage_index=self._find_stage('dof', stages=new_preset )
            if stage_index:
                self._set_filter(filter_dict=None, stage=stage_index, stages=new_preset)
        self._fix_last_stage_input(new_preset)
        #tell the renderer something changed
        deferred_renderer.reset_filters(new_preset)
        #write the new config
        self.write_graphics_config(new_preset, deferred_renderer.shadow_size, deferred_renderer.shading_setup, 'data/user/presets/custom.ini')
        Config.set('graphics','preset', 'custom')
        self.update_options_highlight()

    def set_chroma(self):
        #we put in chroma before forward_mix
        stage_index=self._find_stage('chroma')
        new_preset=copy(deferred_renderer.filter_stages)
        if stage_index is None:
            if 'name' in new_preset[-3]:
                tex_name=new_preset[-3]['name']
            else:
                tex_name=new_preset[-3]['shader']
            chroma_stage={'shader':'chroma',
                        'translate_tex_name':{tex_name:'input_tex'}}
            f_mix_stage_index=self._find_stage('pre_aa', stages=new_preset )
            self._set_filter(filter_dict=chroma_stage, stage=f_mix_stage_index, stages=new_preset)
        else:
            self._set_filter(filter_dict=None, stage=stage_index, stages=new_preset)
        self._fix_last_stage_input(new_preset)
        #tell the renderer something changed
        #deferred_renderer.reset_filters(new_preset)
        #write the new config
        self.write_graphics_config(new_preset, deferred_renderer.shadow_size, deferred_renderer.shading_setup, 'data/user/presets/custom.ini')
        Config.set('graphics','preset', 'custom')
        deferred_renderer.reset_filters(new_preset)
        self.update_options_highlight()


    def set_ao(self):
        stage_index=self._find_stage('ao')
        new_preset=copy(deferred_renderer.filter_stages)
        if stage_index is None:
            ao_stage={'name':'ao_basic',
                      'shader': 'ao',
                      'inputs': {'random_tex': 'tex/noise.png',
                                 'sample_rad' : 0.015,
                                 'strength' : 0.7,
                                 'falloff' : 1.0,
                                 'amount' : 1.1}}
            blur_stage={'name': 'ao',
                        'translate_tex_name': {'ao_basic': 'input_tex'},
                        'shader': 'blur',
                        'inputs': {'blur': 2.5},
                        'size': 0.5}
            self._set_filter(filter_dict=ao_stage, define=(('mix', 'DISABLE_AO', None),), stages=new_preset)
            self._set_filter(filter_dict=blur_stage, stage=2, stages=new_preset)
        else:
            self._set_filter(filter_dict=None, define=(('mix', 'DISABLE_AO', 1),), stage=stage_index, stages=new_preset)
            stage_index=self._find_stage('ao', stages=new_preset )
            if stage_index:
                self._set_filter(filter_dict=None, stage=stage_index, stages=new_preset)
        #tell the renderer something changed
        deferred_renderer.reset_filters(new_preset)
        #write the new config
        self.write_graphics_config(new_preset, deferred_renderer.shadow_size, deferred_renderer.shading_setup, 'data/user/presets/custom.ini')
        Config.set('graphics','preset', 'custom')
        self.update_options_highlight()


    def _fix_last_stage_input(self, stages):
        #stages[-1] is fxaa
        #stages[-2] is forward mix
        #we need the name/shader name of stages[-3]
        if 'name' in stages[-3]:
            tex_name=stages[-3]['name']
        else:
            tex_name=stages[-3]['shader']
        stages[-2]['translate_tex_name'] = {tex_name: 'input_tex'}

    def _find_stage(self, stage_name_or_shader, stages=None):
        if stages is None:
            stages=deferred_renderer.filter_stages
        for n, stage in enumerate(stages):
            if stage['shader'] == stage_name_or_shader:
                return n
            elif 'name' in stage:
                if stage['name'] == stage_name_or_shader:
                    return n
        return None

    def _set_define(self, stage_name, name, value, stages=None):
        if stages is None:
            stages=deferred_renderer.filter_stages
        stage_index=self._find_stage(stage_name, stages)
        if stage_index is not None:
            if 'define' in stages[stage_index]:
                if name in stages[stage_index]['define'] and value is None:
                    del stages[stage_index]['define'][name]
                else:
                    stages[stage_index]['define'][name]=value
            else:
                if value is not None:
                    stages[stage_index]['define']={name:value}

    def _set_filter(self, filter_dict, define=None, stage=1, stages=None):
        if stages is None:
            stages=deferred_renderer.filter_stages
        #insert or remove the new stage
        if filter_dict is None:
            del stages[stage]
        else:
            stages.insert(stage, filter_dict)
        #update definea
        if define:
            for (stage_name, name, value) in define:
                self._set_define(stage_name, name, value, stages=stages)

    def change_filter_setting(self, name, setting, value, min=0.0, max=1.0):
        value=min + value * (max-min)
        deferred_renderer.set_filter_input(name, setting, value, operator.add)
        #print(name, setting, deferred_renderer.get_filter_input(name, setting).get_vector()[0])

    def set_shadows(self, shadow_size=0):
        #tell the renderer to make future lights with right shadows
        deferred_renderer.shadow_size=shadow_size
        #set the existing light shadows
        game.light_1.set_shadow_size(shadow_size)
        #write the new config
        self.write_graphics_config(deferred_renderer.filter_stages, deferred_renderer.shadow_size, deferred_renderer.shading_setup, 'data/user/presets/custom.ini')
        Config.set('graphics','preset', 'custom')
        #update gui
        game.gui.highlight(name='hi_shadow_button', on=False)
        game.gui.highlight(name='med_shadow_button', on=False)
        game.gui.highlight(name='lo_shadow_button', on=False)
        game.gui.highlight(name='no_shadow_button', on=False)
        if shadow_size >= 1024:
            game.gui.highlight(name='hi_shadow_button', on=True)
        elif shadow_size == 512:
            game.gui.highlight(name='med_shadow_button', on=True)
        elif shadow_size == 256:
            game.gui.highlight(name='lo_shadow_button', on=True)
        elif shadow_size == 0:
            game.gui.highlight(name='no_shadow_button', on=True)

    def set_preset(self, preset_name, show_hide=None):
        ini_file=get_local_file('presets/'+preset_name+'.ini')
        preset, setup, shadows = self.read_graphics_config(ini_file)
        deferred_renderer.reset_filters( preset, setup)
        deferred_renderer.shadow_size=shadows
        #set the existing light shadows
        game.light_1.set_shadow_size(shadows)

        if show_hide:
            game.gui.show_hide(*show_hide)
        Config.set('graphics','preset', preset_name)

        render_size=1
        if 'FORWARD_SIZE' in setup:
            render_size=setup['FORWARD_SIZE']
        self.update_options_highlight()

    def set_win_size(self, x, y, fullscreen=0):
        wp = WindowProperties.getDefault()
        if fullscreen == 1:
            mods=[]
            for mode in base.pipe.get_display_information().get_display_modes():
                mods.append((mode.width, mode.height))
            if (x,y) not in mods:
                print ("Can't open fullscreen window at", x,'x',y)
                return
            wp.setFullscreen(True)
        else:
            wp.setFullscreen(False)
        wp.set_size(x,y)
        WindowProperties.set_default(wp)
        base.win.request_properties(wp)
        base.graphicsEngine.render_frame()
        base.win.request_properties(wp)
        Config.set('graphics','fullscreen', str(fullscreen))
        Config.set('graphics','win-size', '{} {}'.format(x,y))

    #key binds...
    def update_gui_key_names(self):
        '''Updates the text on keybinds buttons'''
        #remove old txt
        for name in copy(game.gui.elements):
            if name.startswith('extra_txt'):
                try:
                    game.gui[name].remove_node()
                except:
                    pass
                del game.gui.elements[name]
        #add new txt
        for name in copy(game.gui.elements):
            #all the buttons that need this update are parented to the 'controls' frame
            #so we can find them by name
            if name.startswith('controls_button_'):
                button=game.gui[name]
                #voodoo here!
                #the buttons have a cmd like "game.show_bind_key('some_action')"
                #all this here is to get what the 'some_action' is
                callback=messenger._Messenger__callbacks[(button.getAllAccepting()[0])]
                for value in callback.values():
                    bindname=value[1][1].split("'")[1]
                #make a txt obj
                game.gui.text(txt=Config.get('keys', bindname), pos=(292,0), parent=name, align='right', big_font=False, mono_font=False, wordwrap=None, name='extra_txt'+name)
                #base_txt=button['text'].split(':')[0] #the old text is 'Name-of-the-action: key-name'
                #txt=base_txt+":{:>"+str(24-len(base_txt))+"}"
                #button['text']=txt.format(Config.get('keys', bindname))

    def show_bind_key(self, bindname):
        '''Shows the keybind frame and starts listening for key press'''
        game.gui.show_hide('keybind','controls')
        self.last_keyname=Config.get('keys', bindname)
        game.gui['txt_bind_input'].node().set_text(self.last_keyname)
        base.buttonThrowers[0].node().setButtonDownEvent('buttonDown')
        self.accept('buttonDown', self.get_key)
        self.last_bindname=bindname


    def cancel_bind(self):
        '''Hides the keybind frame and stops listening for keys '''
        game.gui.show_hide('controls','keybind')
        base.buttonThrowers[0].node().setButtonDownEvent('')
        self.ignore('buttonDown')

    def get_key(self, keyname):
        game.gui['txt_bind_input'].set_text(keyname)
        self.last_keyname=keyname

    def bind_last_key(self):
        game.gui.show_hide('controls','keybind')
        base.buttonThrowers[0].node().setButtonDownEvent('')
        self.ignore('buttonDown')
        Config.set('keys', self.last_bindname, self.last_keyname)
        self.update_gui_key_names()

    #read and write ini files/values
    def _encode_ini_value(self, var):
        var_type=type(var)
        if var_type is type(Vec4()) or var_type is type(Vec3()) or  var_type is type(Vec2()) or var_type is type([]):
            return ', '.join([str(i) for i in var])
        if  var_type is type({}):
            combined=''
            for name, value in var.items():
                combined+=name+' : '+self._encode_ini_value(value)+'\n'
            return combined[:-1]
        if  var_type is type(Texture()):
            return '/'.join(str(var.get_filename()).split('/')[-2:])
        return str(var)

    def _decode_ini_value(self, var):
        if type(var) is type([]):
            if len(var) == 2:
                return Vec2(*(float(i) for i in var))
            elif len(var) == 3:
                return Vec3(*(float(i) for i in var))
            elif len(var) == 4:
                return Vec4(*(float(i) for i in var))
        try:
            return int(var)
        except ValueError:
            try:
                return float(var)
            except ValueError:
                return var

    def write_graphics_config(self, preset, shadows, setup, config_file):
        cfg=configparser.ConfigParser()
        cfg.add_section('SHADOWS')
        cfg.set('SHADOWS', 'size', str(shadows))
        cfg.add_section('SETUP')
        for name, value in setup.items():
            cfg.set('SETUP', str(name), str(value))
        for i, item in enumerate(preset):
            cfg.add_section(str(i))
            for name, value in item.items():
                cfg.set(str(i), name, self._encode_ini_value(value))
        with open(config_file, 'w') as f:
            cfg.write(f)

    def read_graphics_config(self, config_file):
        gfx_config = configparser.ConfigParser()
        try:
            gfx_config.read(config_file)
        except:
            return None, None
        preset=[x for x in gfx_config.sections() if x  not in ('SETUP','SHADOWS')]
        setup={}
        shadows_size=256
        for section in gfx_config.sections():
            section_dict={}
            for option in gfx_config.options(section):
                if option in  ('inputs', 'translate_tex_name', 'define'):
                    inputs={}
                    for line in gfx_config.get(section, option).split('\n'):
                        if line:
                            item=line.split(':')
                            key=item[0].strip()
                            value=item[1].split(',')
                            if len(value) == 1:
                                value=value[0].strip()
                            else:
                                value=[x.strip() for x in value]
                            inputs[key]=self._decode_ini_value(value)
                    section_dict[option]=inputs
                else:
                    section_dict[option]=self._decode_ini_value(gfx_config.get(section, option))
            if section == 'SETUP':
                setup={key.upper():value for key, value in section_dict.items()}
            elif section == 'SHADOWS':
                shadows_size=section_dict['size']
            else:
                preset[int(section)]=section_dict
        return preset, setup, shadows_size
