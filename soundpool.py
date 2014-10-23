'''
    Avolotion
    Copyright (C) 2014  Grzegorz 'Wezu' Kalinski grzechotnik1984@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
''' 

from panda3d.core import *

class SoundPool():
    def __init__(self, common):
        self.audio3d=common['audio3d'] 
        self.sound_nodes=[]
        self.free_nodes=[]
        self.sounds=[]
        for node in range(11):            
            self.sound_nodes.append(render.attachNewNode("soundNode"+str(node)))
            self.free_nodes.append(node)
            self.sounds.append({'hit1':self.audio3d.loadSfx("sfx/hit1.ogg"),                    
                                'hit2':self.audio3d.loadSfx("sfx/hit2.ogg"),
                                'hit3':self.audio3d.loadSfx("sfx/hit3.ogg"),
                                'hit_arrow':self.audio3d.loadSfx("sfx/arrow_hit.ogg"),
                                'hit_arrow_bone':self.audio3d.loadSfx("sfx/arrow_bone.ogg"),
                                'hit_arrow_metal':self.audio3d.loadSfx("sfx/arrow_metal.ogg"),
                                'hit_arrow_rock':self.audio3d.loadSfx("sfx/arrow_rock.ogg"),
                                'hit_metal':self.audio3d.loadSfx("sfx/hit_metal.ogg"),
                                'hit_rock':self.audio3d.loadSfx("sfx/hit_rock.ogg"),
                                'die1':self.audio3d.loadSfx("sfx/die1.ogg"), 
                                'die2':self.audio3d.loadSfx("sfx/die2.ogg"), 
                                'die3':self.audio3d.loadSfx("sfx/die3.ogg"), 
                                'die4':self.audio3d.loadSfx("sfx/die4.ogg"), 
                                'die5':self.audio3d.loadSfx("sfx/die5.ogg"), 
                                'die6':self.audio3d.loadSfx("sfx/die6.ogg"), 
                                'die7':self.audio3d.loadSfx("sfx/die7.ogg"), 
                                'onFire':self.audio3d.loadSfx("sfx/flame2.ogg"),
                                'die_metal':self.audio3d.loadSfx("sfx/die_metal.ogg"), 
                                'spark':self.audio3d.loadSfx("sfx/spark.ogg")})
            for sound in self.sounds[-1]:
                self.audio3d.attachSoundToObject(self.sounds[-1][sound], self.sound_nodes[-1])
        self.targets={}            
        taskMgr.add(self.update, "soundPoolTask")
    
    def play(self, id, sound):
        #print id, " plays:",  sound
        self.sounds[id][sound].play()
        
    def get_id(self):
        if len(self.free_nodes)>0:
            return self.free_nodes.pop()
        else:
            raise Exception("Out of sound pools")
            
    def set_target(self, id, node):
        self.targets[id]=node
    
    def set_free(self,id):
        if id in self.free_nodes:
            return
        self.free_nodes.append(id)
        self.targets.pop(id)
        
    def update(self, task):
        for target in self.targets:
            if self.targets[target]:
                self.sound_nodes[target].setPos(self.targets[target].getPos(render))
        return task.again 



class SoundPool2D():
    def __init__(self):        
        self.sound_nodes=[]
        self.free_nodes=[]
        self.sounds=[]
        for node in range(11):            
            self.sound_nodes.append(render.attachNewNode("soundNode"+str(node)))
            self.free_nodes.append(node)
            self.sounds.append({'hit1':base.loader.loadSfx("sfx/hit1.ogg"),                    
                                'hit2':base.loader.loadSfx("sfx/hit2.ogg"),
                                'hit3':base.loader.loadSfx("sfx/hit3.ogg"),
                                'hit_metal':base.loader.loadSfx("sfx/hit_metal.ogg"),
                                'hit_rock':base.loader.loadSfx("sfx/hit_rock.ogg"),
                                'die1':base.loader.loadSfx("sfx/die.ogg"), 
                                'die2':base.loader.loadSfx("sfx/die2.ogg"), 
                                'die3':base.loader.loadSfx("sfx/die3.ogg"), 
                                'die4':base.loader.loadSfx("sfx/die4.ogg"), 
                                'spark':base.loader.loadSfx("sfx/spark.ogg")})            
        self.targets={}            
        taskMgr.add(self.update, "soundPoolTask")
    
    def play(self, id, sound):
        print id, " plays:",  sound
        self.sounds[id][sound].play()
        #todo: adjust volume based on direction and distance... how?
        print self.sound_nodes[id].getDistance(base.camera)
        print self.sound_nodes[id].getHpr(render)-base.camera.getHpr(render)
        
    def get_id(self):
        if len(self.free_nodes)>0:
            return self.free_nodes.pop()
        else:
            raise Exception("Out of sound pools")
            
    def set_target(self, id, node):
        self.targets[id]=node
    
    def set_free(self,id):
        self.free_nodes.append(id)
        self.targets[id]=None
        
    def update(self, task):
        for target in self.targets:
            if self.targets[target]:
                self.sound_nodes[target].setPos(self.targets[target].getPos(render))
                self.sound_nodes[target].lookAt(base.camera)
        return task.again 