'''Avolition 2.0
INFO:
    This module is the glue that holds the game together.
    It loads and initiates all the needed components (modules)
    and makes the instances visible to each other (eg. the Level instance is visible as game.level)
    It holds some commonly used functions and functions that don't fit any other component.
    It also holds info about levels(eg. what model to use for level 7, what monsters are on lv1 etc),
    and monsters (model, anims, speed, damage, sound names, etc )
    This module is imported by main.py
    Import graph:
    App(main.py)
        |-Game(game.py)
            |-Players
            |   |-pc_*.py
            |       |-Vfx
            |       |-SphereLight
            |       |-Projectile
            |
            |-Monster
            |-Level
            |-Audio
            |-loading
            |-CameraControler
            |-Vfx
            |-UI
            |-SphereLight
            |-SceneLight
            |-DeferredRenderer
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
#panda3d imports
from panda3d.core import *
from panda3d.bullet import *
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import *

#load the main components
from deferred_render import *
from camera import CameraControler
from options import Options
from loading_screen import loading
from ui import UI
from level import Level
from vfx import Vfx
from vfx import Lightning
from audio import Audio
from monster import Monster
from players import Players

import os
import random
import builtins
import json
from collections import namedtuple


def get_local_file(path):
    return getModelPath().findFile(path).toOsSpecific()

#this is used for ray tests return values
Hit = namedtuple('Hit', 'pos node')

#Start the game
class Game(DirectObject):
    def __init__(self, app):
        self.app=app
        builtins.get_local_file = get_local_file
        #insert the game into buildins for easy gui callback
        builtins.game=self

        #load things, but show a loading screen while loading
        with loading():
            #setup bullet
            self.world_np = render.attach_new_node('World')
            #debug stuff
            self.debug_np = self.world_np.attach_new_node(BulletDebugNode('Debug'))
            self.debug_np.node().show_wireframe(True)
            self.debug_np.node().show_constraints(True)
            self.debug_np.node().show_bounding_boxes(False)
            self.debug_np.node().show_normals(False)
            #the bullet world
            self.world = BulletWorld()
            self.world.set_gravity(Vec3(0, 0, -9.81))
            self.world.set_debug_node(self.debug_np.node())
            #self.debug_np.show()

            #collision masks
            floor =0
            wall =1
            monster=2
            other=3
            player=4
            weapon=5
            monster_weapon=6
            #bit masks used for collisions
            #this grew over time, maybe it's no good?
            Masks = namedtuple('Masks', 'floor wall monster other player weapon  monster_weapon weapon_ray')
            self.bit_mask=Masks(*(BitMask32() for i in range(8)))
            self.bit_mask.floor.set_bit(floor)
            self.bit_mask.wall.set_bit(wall)
            self.bit_mask.monster.set_bit(monster)
            self.bit_mask.other.set_bit(other)
            self.bit_mask.player.set_bit(player)
            self.bit_mask.weapon.set_bit(weapon)
            self.bit_mask.monster_weapon.set_bit(monster_weapon)
            self.bit_mask.weapon_ray.set_range(0,3) #because fuck logic

            self.world.set_group_collision_flag(player, floor, False)
            self.world.set_group_collision_flag(player, wall, True)
            self.world.set_group_collision_flag(player, monster, True)
            self.world.set_group_collision_flag(player, other, False)

            self.world.set_group_collision_flag(weapon, floor, True)
            self.world.set_group_collision_flag(weapon, wall, True)
            self.world.set_group_collision_flag(weapon, monster, True)
            self.world.set_group_collision_flag(weapon, other, False)
            self.world.set_group_collision_flag(weapon, player, False)

            self.world.set_group_collision_flag(monster_weapon, player, True)
            self.world.set_group_collision_flag(monster_weapon, floor, False)
            self.world.set_group_collision_flag(monster_weapon, wall, False)
            self.world.set_group_collision_flag(monster_weapon, monster, False)
            self.world.set_group_collision_flag(monster_weapon, other, False)

            #get the preset and setup for deferred rendering and set it up
            self.options=Options()
            ini_file=get_local_file('presets/'+Config.get('graphics', 'preset')+'.ini')
            preset, setup, shadows = self.options.read_graphics_config(ini_file)
            DeferredRenderer(filter_setup=preset, shading_setup=setup, shadows=shadows)
            deferred_renderer.set_near_far(1.0,100.0)

            #set lights
            self.light_0 = SceneLight(color=(0.0, 0.0, 0.0), direction=Vec3(0.1, -0.5, 1.0), shadow_size=0)
            self.light_1 = SphereLight(color=(0.6,0.4,0.2), pos=(0,0,1.8), radius=10.0, shadow_bias=0.0089)

            #init camera control
            self.cam=CameraControler(pos=(0,0,1.5),
                                     offset=(0, 7, 2.0),
                                     speed=0.25,
                                     zoom_speed=0.03,
                                     limits=(3.0, 15.0, -50, 30))
            self.cam.node.set_h(180)
            #self.cam.bind_keys()
            #self.light_1.attach_to(self.cam.node, Point3(0, 1.0, 2.5))

            #load level loader
            self.level=Level(deferred_render)
            self.monsters=set()
            self.dead_monsters=set()

            #load sounds
            self.audio=Audio()

            sound_dirs=set(getModelPath().findAllFiles('sfx/'))
            sounds={}
            for dir in sound_dirs:
                for filename in os.listdir(get_local_file(dir)):
                    sounds[filename[:-4]]='sfx/'+filename
            self.audio.load_sounds(sounds)

            #load music
            #self.audio.load_music(('music/LuridDeliusion.ogg',),'menu')
            music_dirs=set(getModelPath().findAllFiles('music/'))
            for dir in music_dirs:
                for dir_name in os.listdir(get_local_file(dir)):
                    full_path=os.path.abspath(dir+dir_name)
                    if os.path.isdir(full_path):
                        music=[]
                        for filename in os.listdir(full_path):
                            music.append(str(Filename.from_os_specific(os.path.join(full_path,filename))))
                        #print(dir_name, music)
                        self.audio.load_music(music,dir_name)
            #init the gui system
            self.gui=UI()
            self.gui.load_from_file(get_local_file('ui/gui.json'))
            #update the text on gui buttons
            self.options.update_gui_key_names()
            self.options.update_options_highlight()

            #chargen
            self.level.load('models/tiles/camp.egg')
            self.pc=Players()

            self.sparks=Vfx('vfx/sparks_up.png', loop=True, fps=30.0)
            self.sparks.set_scale(3.0)
            self.sparks.set_pos(0,0,0.9)

            self.fire=Vfx('vfx/big_fire3.png', loop=True, fps=60.0)
            self.fire.set_scale(2.0)
            self.fire.set_pos(0,0,0.47)

            self.seq= Sequence(LerpHprInterval(self.cam.node, 18.0, (225, 10, 0), (135,-10,0), blendType='easeInOut'),
                               LerpHprInterval(self.cam.node, 18.0, (135, -10, 0), (225,10,0), blendType='easeInOut'))

            ##for tests
            '''self.level.load('models/tiles/level1.egg',
                            'models/tiles/navmesh.egg',
                            'models/tiles/level1/face_#.png')

            #pc -this broken, use self.pc['???'] or something?
            self.pc=Witch(node=self.cam.node)

            #npc
            self.m1=Monster(model='models/npc/m_golem_gold',
                            anims={'attack':'models/npc/a_golem2_attack',
                                   'attack1':'models/npc/a_golem2_attack1',
                                   'die':'models/npc/a_golem2_die',
                                   'walk':'models/npc/a_golem2_walk',
                                   'idle':'models/npc/a_golem2_walk'},
                            scale=0.4,
                            move_speed=1.5,
                            play_rates={'walk': 2.0})
            self.m1.set_pos(0, 10, 0)'''

        #loading is done, fade from black
        self.gui.fade()
        self.gui['main_menu'].show()
        #run the camera sequence
        self.seq.loop()
        self.seq.set_t(6.0)
        #set the camera mouse control to 3rd person mode
        self.camera_mouse_mode(False)
        self.audio.play_music('menu')
        #self.accept('escape', self.camera_mouse_mode)

        #add update task
        taskMgr.add(self.update, "game_update")

    def find_saves(self):
        pass

    def load_game(self, savefile):
        pass

    def save_game(self, slot):
        pass

    def select_class(self, class_name):
        self.gui.show_hide('chargen_'+class_name, 'chargen')
        if class_name in self.pc:
            self.pc[class_name].on_select()
            self.gui[class_name+'_stats'].node().set_text(self.pc[class_name].get_stats_string())

    def set_skill(self, class_name, skill1, skill2, value):
        if class_name in self.pc:
            self.pc[class_name].set_skills(skill1, skill2, value)
            self.gui[class_name+'_stats'].node().set_text(self.pc[class_name].get_stats_string())

    def chargen_back(self):
        for class_name, pc in self.pc.items():
            self.gui.show_hide('', 'chargen_'+class_name)
            self.gui['chargen_skills1_'+class_name]['value']=0.5
            self.gui['chargen_skills2_'+class_name]['value']=0.5
            self.gui['chargen_skills3_'+class_name]['value']=0.5
        self.gui.show_hide('chargen')
        self.aoe_test((-1,1,0), 1.0)

    def update(self, task):
        dt = globalClock.getDt()
        game.world.do_physics(dt)
        if int(globalClock.get_frame_time()*100) % 10 ==0:
            self.light_1.set_pos(random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05), random.uniform(1.75, 1.8))
            self.light_1.set_color(Vec3(0.6,0.4,0.2)*random.uniform(0.7, 1.0))
        return task.again

    def do_nill(self, *args):
        pass

    def camera_ray_test(self, mask=None):
        """Find the first object (and point) under the croshair """
        m_pos=game.gui.croshair.get_pos(render2d)
        from_point = Point3()
        to_point = Point3()
        base.camLens.extrude(Point2(0, m_pos.z), from_point, to_point)
        # Transform to global coordinates
        from_point = render.get_relative_point(base.cam, from_point)
        to_point = render.get_relative_point(base.cam, to_point)
        #move from_point closer to to_point
        from_point+=(to_point-from_point).normalized()*self.pc.node.get_distance(base.camera)*0.7
        return self.ray_test(from_point, to_point, mask)

    def ray_test(self, from_point, to_point, mask=None):
        """Find the first object (and point) on the from_point-to_point line """
        result= self.world.ray_test_closest(from_point, to_point, mask)
        if result.has_hit():
            return Hit(result.get_hit_pos(), result.get_node())
        else:
            return None

    def aoe_test(self, from_point, radius):
        hits=set()
        final_hits=[]
        np = self.world_np.attach_new_node(BulletRigidBodyNode('aoe'))
        np.node().add_shape(BulletSphereShape(radius))
        np.node().set_kinematic(True)
        np.set_pos(from_point)
        np.set_collide_mask(self.bit_mask.monster|self.bit_mask.player)
        self.world.attach_rigid_body(np.node())
        test=self.world.contact_test(np.node())
        for contact in test.get_contacts():
            node=NodePath().any_path(contact.get_node0())
            hits.add(node)
        #confirm hits
        for np in hits:
            if np.has_python_tag('node'):
                target=np.get_python_tag('node')
                to_point=target.node.get_pos(render)
                hit=self.ray_test(from_point, to_point, self.bit_mask.weapon_ray)
                if hit:
                    if hit.node.has_python_tag('node'):
                        if target == hit.node.get_python_tag('node'):
                            final_hits.append(hit)
        return final_hits

    def camera_mouse_mode(self, active=None):
        """Turn on/off the camera control and hide/show the cursor/croshair """
        if active is None:
            active=not self.cam.active
        if not active:
            self.cam.set_active(False)
            self.gui.croshair.hide()
            wp = WindowProperties(base.win.getRequestedProperties())
            wp.set_cursor_hidden(False)
            base.win.request_properties(wp)
        else:
            self.cam.set_active()
            self.gui.croshair.show()
            wp = WindowProperties(base.win.getRequestedProperties())
            wp.set_cursor_hidden(True)
            base.win.request_properties(wp)

    def exit_game(self):
        with open('config.ini', 'w') as config_filename:
            Config.write(config_filename)
        self.app.final_exit()
