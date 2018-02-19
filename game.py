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


#reading the config file
from panda3d.core import loadPrcFileData
loadPrcFileData('','cursor-hidden 1')
loadPrcFileData('','screenshot-extension jpg')
#loadPrcFileData('','show-frame-rate-meter  1')
loadPrcFileData('','screenshot-filename %~p%d-%m-%y-%H.%M.%S.%~e')
from direct.showbase.AppRunnerGlobal import appRunner


if appRunner: #run from binary
    path=appRunner.p3dFilename.getDirname()+'/'#+'/autoconfig.txt'
else:  #run from python
    path=''#'autoconfig.txt'
try:
    f = open(path+'autoconfig.txt', 'r')
    for line in f:
        if not line.startswith('#'):
            loadPrcFileData('',line)
except IOError:
    print("No config file, using default")
try:
    f = open(path+'config.txt', 'r')
    for line in f:
        if not line.startswith('#'):
            loadPrcFileData('',line)
except IOError:
    print("No custom config file")


from panda3d.core import WindowProperties
from panda3d.core import ConfigVariableInt
from panda3d.core import ConfigVariableBool
from panda3d.core import ConfigVariableString
config_nude=ConfigVariableInt('loverslab', 0)
config_aa=ConfigVariableInt('multisamples', 0)
buff_size=ConfigVariableInt('buffer-size', 1024)
config_fulscreen=ConfigVariableBool('fullscreen')
config_win_size=ConfigVariableInt('win-size', '640 480')
config_autoshader=ConfigVariableBool('use-shaders', 0)
config_bloom=ConfigVariableBool('bloom', 1)
config_music=ConfigVariableInt('music-volume', '30')
config_sfx=ConfigVariableInt('sound-volume', '100')
config_safemode=ConfigVariableBool('safemode', 0)
#keys
config_forward=ConfigVariableString('key_forward', 'w|arrow_up')
config_back=ConfigVariableString('key_back', 's|arrow_down')
config_left=ConfigVariableString('key_left', 'a|arrow_left')
config_right=ConfigVariableString('key_right', 'd|arrow_right')
config_camera_left=ConfigVariableString('key_cam_left', 'q|delete')
config_camera_right=ConfigVariableString('key_cam_right', 'e|page_down')
config_action1=ConfigVariableString('key_action1', 'mouse1|enter')
config_action2=ConfigVariableString('key_action2', 'mouse3|space')
config_zoomin=ConfigVariableString('key_zoomin', 'wheel_up|r')
config_zoomout=ConfigVariableString('key_zoomout', 'wheel_down|f')
#if(config_aa.getValue()>0):
#    loadPrcFileData('','multisamples '+str(config_aa.getValue()))
wp = WindowProperties.getDefault()
#wp = base.win.getProperties()
wp.setFixedSize(False)
wp.setCursorHidden(True)
wp.setUndecorated(True)
wp.setOrigin(-2,-2)
wp.setTitle("Avolition - Demo v.1.0, www.indiedb.com/games/avolition/")
if(config_fulscreen.getValue ()==1):
    wp.setFullscreen(True)
wp.setSize(config_win_size.getWord(0),config_win_size.getWord(1))
#WindowProperties.setDefault(wp)
#base.win.requestProperties(wp)


from panda3d.core import *
#import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
from direct.filter.FilterManager import FilterManager
from direct.showbase import Audio3DManager
from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import *
from direct.actor.Actor import Actor
import json
import os
from chargen import CharGen
from soundpool import SoundPool
from engine import Spawner
from engine import LevelLoader


#base.openMainWindow(props = wp)
#wp = base.win.getProperties()
#base.win.requestProperties(wp)
#base.setBackgroundColor(0, 0, 0)
#winX = (wp.getXSize()-800)/2
#winY = (wp.getYSize()-600)/2
#print wp.getXSize(), wp.getYSize()
#print winX, winY
#load_screen = DirectFrame(frameSize=(-1024, 0, 0, 1024),
#                                    frameColor=(1,1,1,1),
#                                    frameTexture='loading.png',
#                                    parent=pixel2d)
#load_screen.setPos(1024+winX,0,-1024-winY)


for i in range(2):
    base.graphicsEngine.renderFrame()


class Game(DirectObject):
    def __init__(self, loadscreen, root):
        self.loadscreen=loadscreen

        #base.openMainWindow()
        if not config_safemode.getValue():
            render.setShaderAuto()
        base.disableMouse()
        #base.setBackgroundColor(0, 0, 0)
        if not config_safemode.getValue():
            if config_aa.getValue()>0:
                render.setAntialias(AntialiasAttrib.MMultisample)
            base.camLens.setNearFar(3, 40)

        self.common={}
        self.common['root']=root
        self.common['safemode']=config_safemode.getValue()
        #print self.common['safemode']
        #keys
        self.common['keymap']={}
        self.common['keymap']['key_forward']=config_forward.getValue().split('|')
        self.common['keymap']['key_back']=config_back.getValue().split('|')
        self.common['keymap']['key_left']=config_left.getValue().split('|')
        self.common['keymap']['key_right']=config_right.getValue().split('|')
        self.common['keymap']['key_cam_left']=config_camera_left.getValue().split('|')
        self.common['keymap']['key_cam_right']=config_camera_right.getValue().split('|')
        self.common['keymap']['key_action1']=config_action1.getValue().split('|')
        self.common['keymap']['key_action2']=config_action2.getValue().split('|')
        self.common['keymap']['key_zoomin']=config_zoomin.getValue().split('|')
        self.common['keymap']['key_zoomout']=config_zoomout.getValue().split('|')
        self.common['extra_ambient']=True
        self.common['nude']=config_nude.getValue()
        self.common['path']=path

        #load save
        levels=[]
        try:
            f = open(path+'save.dat', 'r')
            for line in f:
                levels.append(line)
        except IOError:
            print("No save file")
        self.common['max_level']=len(levels)

        self.common["key_icon"]=DirectFrame(frameSize=(-64, 0, 0, 64),
                                    frameColor=(1, 1, 1, 1),
                                    frameTexture="icon/icon_key2.png",
                                    parent=pixel2d)
        self.common["key_icon"].setPos(64,0,-64)
        self.common["key_icon"].setTransparency(TransparencyAttrib.MDual)
        self.common["key_icon"].hide()

        if config_bloom.getValue():
            self.common['extra_ambient']=False
        if config_safemode.getValue():
            self.common['extra_ambient']=True
        #print "extra ambient:", self.common['extra_ambient']

        #audio 3d
        self.common['audio3d']=Audio3DManager.Audio3DManager(base.sfxManagerList[0], base.camera)
        self.common['audio3d'].setListenerVelocityAuto()
        self.common['audio3d'].setDropOffFactor(0.2)
        self.common['soundPool']=SoundPool(self.common)
        base.sfxManagerList[0].setVolume(config_sfx.getValue()*0.01)
        self.common['click']=base.loader.loadSfx("sfx/click_stereo.ogg")

        #base.cTrav = CollisionTraverser()

        self.common['monsterList']=[]
        self.common['spawner']=Spawner(self.common)
        self.common['levelLoader']=LevelLoader(self.common)

        #self.common['PC']=PC(self.common)
        #self.common['PC'].node.setPos(-12, 0, 0)

        #spawner
        #self.spawner=Spawner(self.common, monster_limit=5, tick=9.13)

        #music

        base.musicManager.setVolume(config_music.getValue()*0.01)
        self.common['musicVolume']=config_music.getValue()
        self.common['soundVolume']=config_sfx.getValue()
        #self.music =    [
        #                base.loadMusic("sfx/LuridDeliusion.ogg"),
        #                base.loadMusic("sfx/DefyingCommodus.ogg"),
        #                base.loadMusic("sfx/DarkDescent.ogg")
                        #base.loadMusic("sfx/DarkAmulet.ogg"),
                        #base.loadMusic("sfx/WastelandShowdown.ogg"),
                        #base.loadMusic("sfx/HeroicDemise.ogg")
        #                ]
        #self.musicSequence=Sequence()
        #for music in self.music:
        #    self.musicSequence.append(SoundInterval(music))
        #self.musicSequence.loop()

        #Monster(data.monsters[2],self.common, self.testPC, (12, -4, 0))


        #self.flask=Interactive(self.common, "flask", (-12, 4, 0), 0.15, "vfx/icon_flask.png", "heal")

        #self.health=Actor("models/health", {"anim":"models/health_anim"})
        #self.health.loop("anim")
        #self.health.reparentTo(render)
        #self.health.setPos(-12, 4, 0)
        #self.health.setScale(0.2)
        #self.health.setLightOff()

        self.common['traverser']=CollisionTraverser("playerTrav")
        self.common['traverser'].setRespectPrevTransform(True)
        self.common['queue'] = CollisionHandlerQueue()

        self.common['CharGen']=CharGen(self.common)

        base.openMainWindow(props = wp)

        #bloom
        if not config_safemode.getValue():
            if config_bloom.getValue():
                self.bloomBuffer=base.win.makeTextureBuffer("bloom", buff_size.getValue(), buff_size.getValue())
                self.bloomBuffer.setSort(-3)
                self.bloomBuffer.setClearColor(Vec4(0,0,0,1))
                self.bloomCamera=base.makeCamera(self.bloomBuffer, lens=base.cam.node().getLens())
                glowShader=loader.loadShader("glowShader.sha")
                tempnode = NodePath(PandaNode("temp node"))
                tempnode.setShader(glowShader)
                self.bloomCamera.node().setInitialState(tempnode.getState())
                self.blurBuffer=self.makeFilterBuffer(self.bloomBuffer,  "Blur X", -2, "blur.sha")
                self.finalcard = self.blurBuffer.getTextureCard()
                self.finalcard.reparentTo(render2d)
                self.finalcard.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
            #shadow buffer
            self.shadowTexture=Texture()
            self.shadowTexture.setWrapU(Texture.WMBorderColor)
            self.shadowTexture.setWrapV(Texture.WMBorderColor)
            self.shadowTexture.setBorderColor(Vec4(1,1,1,1))
            self.shadowBuffer = base.win.makeTextureBuffer("Shadow Buffer",buff_size.getValue(), buff_size.getValue(), self.shadowTexture)
            self.shadowBuffer.setClearColor((1,1,1,1))
            self.shadowCamera = base.makeCamera(self.shadowBuffer)
            self.shadowNode  = render.attachNewNode('shadowNode')
            self.shadowNode.setP(-90)
            #self.shadowNode.setZ(18)
            self.shadowCamera.reparentTo(self.shadowNode)
            #self.shadowCamera.node().showFrustum()
            self.shadow_lens = PerspectiveLens()
            self.shadow_lens.setFov(160)
            self.shadow_lens.setNearFar(0.01,4)
            self.shadowCamera.node().setLens(self.shadow_lens)
            self.shadowCamera.node().setCameraMask(BitMask32.bit(1))
            self.initial = NodePath('initial')
            #self.initial.setTextureOff(2)
            #self.initial.setMaterialOff(2)
            self.initial.setLightOff(2)
            self.initial.setColor(0,0,0,1)
            self.shadowCamera.node().setInitialState(self.initial.getState())
            shadow_manager = FilterManager(self.shadowBuffer, self.shadowCamera)
            sh_tex1 = Texture()
            quad = shadow_manager.renderSceneInto(colortex=sh_tex1)
            quad.setShader(Shader.load("shadow.sha"))
            quad.setShaderInput("tex1", sh_tex1)
            self.shadow_ts=TextureStage('shadow')

            self.common['shadowNode']=self.shadowNode
            self.common['shadow_ts']=self.shadow_ts
            self.common['shadowTexture']=self.shadowTexture
            self.common['shadowCamera']= self.shadowCamera

        taskMgr.add(self.hideLoadscreen, 'hideLoadscreenTask')
        self.accept("x", self.screenshot)

    def screenshot(self):
        #print "cheeese!"
        #base.win.saveScreenshot()
        if os.path.exists(path+'screenshots'):
            base.screenshot(path+'screenshots/')
        else:
            os.makedirs(Filename(path+'screenshots').toOsSpecific())
            base.screenshot(path+'screenshots/')
    def hideLoadscreen(self, task):
        self.loadscreen.hide()
        if base.frameRateMeter:
            #base.frameRateMeter.setAlign(TextNode.ALeft)
            fps_node=NodePath(base.frameRateMeter)
            fps_node.setX(fps_node, -1.75)
        return task.done

    def makeFilterBuffer(self, srcbuffer, name, sort, prog):
        blurBuffer=base.win.makeTextureBuffer(name, 512, 512)
        blurBuffer.setSort(sort)
        blurBuffer.setClearColor(Vec4(0,0,1,1))
        blurCamera=base.makeCamera2d(blurBuffer)
        blurScene=NodePath("new Scene")
        blurCamera.node().setScene(blurScene)
        shader = loader.loadShader(prog)
        card = srcbuffer.getTextureCard()
        card.reparentTo(blurScene)
        card.setShader(shader)
        return blurBuffer


#w = Game()
#run()
