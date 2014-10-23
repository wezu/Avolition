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
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import *
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *
from vfx import vfx
#from vfx import RayVfx
import random, sys
#from levelloader import LevelLoader
from engine import *
from player import *
#from player import PC2
from direct.interval.ActorInterval import ActorInterval
import webbrowser

class CharGen(DirectObject):
    def __init__(self, common):
        self.common=common
        self.common['chargen']=self
        self.load()        
    def load(self):  
        self.font = loader.loadFont('Bitter-Bold.otf')
        self.currentLevel=0
        
        self.common['pc_stat1']=50
        self.common['pc_stat2']=50
        self.common['pc_stat3']=50
        #render.setShaderAuto()
        #base.disableMouse()  
        #render.setAntialias(AntialiasAttrib.MMultisample)
        #base.setBackgroundColor(0, 0, 0)
        wp = base.win.getProperties()
        winX = wp.getXSize()
        winY = wp.getYSize()
        
        
        self.campmap=loader.loadModel("models/camp3")
        self.campmap.reparentTo(render)
        
        #music       
        self.common['music']=MusicPlayer(self.common)
        self.common['music'].loop(0)
        #self.common['music']=base.loadMusic("music/LuridDeliusion.ogg")
        #self.common['music'].setLoop(True)
        #self.common['music'].play()        
        
        
        self.node=render.attachNewNode("node")
        
        self.cameraNode  = self.node.attachNewNode("cameraNode")         
        self.cameraNode.setZ(-1)
        base.camera.setY(-8)
        base.camera.setZ(5)
        base.camera.lookAt((0,3,0))
        base.camera.wrtReparentTo(self.cameraNode)  
        self.pointer=self.cameraNode.attachNewNode("pointerNode") 
        
        #light
        self.pLight = PointLight('plight')
        self.pLight.setColor(VBase4(1, .95, .9, 1))
        self.pLight.setAttenuation(Point3(.5, 0, 0.1))          
        self.pLightNode = self.node.attachNewNode(self.pLight) 
        self.pLightNode.setZ(1.0)
        render.setLight(self.pLightNode)
        
        self.sLight=Spotlight('sLight')
        self.sLight.setColor(VBase4(.4, .25, .25, 1))
        if self.common['extra_ambient']:            
            self.sLight.setColor(VBase4(.7, .5, .5, 1))        
        spot_lens = PerspectiveLens()
        spot_lens.setFov(40)        
        self.sLight.setLens(spot_lens)
        self.Ambient = self.cameraNode.attachNewNode( self.sLight)
        self.Ambient.setPos(base.camera.getPos(render))
        self.Ambient.lookAt((0,3,0))
        render.setLight(self.Ambient)
        
        self.fire_node=self.node.attachNewNode("fireNode")    
        self.fire=vfx(self.fire_node, texture='vfx/big_fire3.png',scale=.29, Z=.5, depthTest=True, depthWrite=True)
        self.fire.show()
        self.fire.loop(0.02) 
        
        self.character1=Actor("models/pc/male", {"attack":"models/pc/male_attack2","idle":"models/pc/male_ready2", "block":"models/pc/male_block"}) 
        self.character1.reparentTo(self.node)
        self.character1.setBlend(frameBlend = True)  
        self.character1.setPos(1,2, 0)
        self.character1.setScale(.025)
        self.character1.setH(-25.0)       
        self.character1.setBin("opaque", 10)
        self.character1.loop("idle")        
        self.swingSound = base.loader.loadSfx("sfx/swing2.ogg")
        
        
        coll_sphere=self.node.attachNewNode(CollisionNode('monsterSphere'))
        coll_sphere.node().addSolid(CollisionSphere(1, 2, 1, 1))   
        coll_sphere.setTag("class", "1") 
        coll_sphere.node().setIntoCollideMask(BitMask32.bit(1))
        
        
        if self.common['nude']:
            self.character2=Actor("models/pc/female_nude", {"attack":"models/pc/female_attack1","idle":"models/pc/female_idle"}) 
        else:    
            self.character2=Actor("models/pc/female", {"attack":"models/pc/female_attack1","idle":"models/pc/female_idle"}) 
        #self.character2.setPlayRate(.4, "attack")
        self.character2.reparentTo(self.node)
        self.character2.setBlend(frameBlend = True)  
        self.character2.setPos(-1,2, 0)
        self.character2.setScale(.026)
        self.character2.setH(25.0)       
        #self.character2.setBin("opaque", 10)
        self.character2.loop("idle")
        
        self.char2_magic= loader.loadModel('vfx/vfx3')
        self.char2_magic.setPos(self.character2.getPos())
        self.char2_magic.setH(self.character2.getH())
        self.char2_magic.setP(-10.0)
        self.char2_magic.setZ(0.71)
        self.char2_magic.setScale(1,2,1)
        self.char2_magic.wrtReparentTo(self.character2)
        self.char2_magic.setY(-10)        
        self.char2_magic.setDepthWrite(False)
        self.char2_magic.setDepthTest(False)
        self.char2_magic.setLightOff()
        self.char2_magic.hide()        
        self.vfxU=-0.125
        self.vfxV=0
        self.magicSound = base.loader.loadSfx("sfx/thunder3.ogg")
        
        coll_sphere=self.node.attachNewNode(CollisionNode('monsterSphere'))
        coll_sphere.node().addSolid(CollisionSphere(-1, 2, 1, 1))   
        coll_sphere.setTag("class", "2") 
        coll_sphere.node().setIntoCollideMask(BitMask32.bit(1))
        
        if self.common['nude']:
            self.character3=Actor("models/pc/female2_nude", {"attack":"models/pc/female2_arm","reset":"models/pc/female2_fire","idle":"models/pc/female2_idle"}) 
        else:    
            self.character3=Actor("models/pc/female2", {"attack":"models/pc/female2_arm","reset":"models/pc/female2_fire","idle":"models/pc/female2_idle"}) 
        #self.character2.setPlayRate(.4, "attack")
        self.character3.reparentTo(self.node)
        self.character3.setBlend(frameBlend = True)  
        self.character3.setPos(-1.8,0.9, 0)
        self.character3.setScale(.026)
        self.character3.setH(40.0)       
        #self.character2.setBin("opaque", 10)
        self.character3.loop("idle")
        
        coll_sphere=self.node.attachNewNode(CollisionNode('monsterSphere'))
        coll_sphere.node().addSolid(CollisionSphere(-1.8,0.9, 0, 1))   
        coll_sphere.setTag("class", "3") 
        coll_sphere.node().setIntoCollideMask(BitMask32.bit(1))
        
        self.arrow_bone=self.character3.exposeJoint(None, 'modelRoot', 'arrow_bone')
        self.arrow=loader.loadModel('models/arrow')        
        self.arrow.reparentTo(self.arrow_bone)
        self.arrow.setP(-45)
        self.movingArrow=None
        self.arrowTime=0.0
        self.drawSound = base.loader.loadSfx("sfx/draw_bow2.ogg")
        self.fireSound = base.loader.loadSfx("sfx/fire_arrow3.ogg")
        
        
        self.character4=Actor("models/pc/male2", {"attack":"models/pc/male2_aura","idle":"models/pc/male2_idle"}) 
        #self.character2.setPlayRate(.4, "attack")
        self.character4.reparentTo(self.node)
        self.character4.setBlend(frameBlend = True)  
        self.character4.setPos(1.8,0.9, 0)
        self.character4.setScale(.024)
        self.character4.setH(-60.0)       
        #self.character2.setBin("opaque", 10)
        self.character4.loop("idle")
        self.FFSound = base.loader.loadSfx("sfx/teleport.ogg")
        #self.FFSound = base.loader.loadSfx("sfx/walk_new3.ogg")
        
        coll_sphere=self.node.attachNewNode(CollisionNode('monsterSphere'))
        coll_sphere.node().addSolid(CollisionSphere(1.8,0.9, 0, 1))   
        coll_sphere.setTag("class", "4") 
        coll_sphere.node().setIntoCollideMask(BitMask32.bit(1))
        
        
        
        #gui
        self.mp_logo=DirectFrame(frameSize=(-512, 0, 0, 128),
                                    frameColor=(1,1,1, 1),
                                    frameTexture='mp_logo.png',
                                    state=DGG.NORMAL,
                                    parent=pixel2d)       
        self.mp_logo.setPos(256+winX/2, 0, -winY)
        self.mp_logo.setBin('fixed', 1)
        self.mp_logo.hide()
        self.mp_logo.setTransparency(TransparencyAttrib.MDual)
        self.mp_logo.bind(DGG.B1PRESS, self.open_www, ['http://www.matthewpablo.com/'])
        #self.mp_logo.bind(DGG.WITHIN, self.GUIOnEnter, ["MP"]) 
        #self.mp_logo.bind(DGG.WITHOUT, self.GUIOnExit)
        
        self.title = DirectFrame(frameSize=(-512, 0, 0, 128),
                                    frameColor=(1,1,1, 1),
                                    frameTexture='select.png',
                                    parent=pixel2d)       
        self.title.setPos(256+winX/2, 0, -128)
        self.title.setBin('fixed', 1)
        self.title.setTransparency(TransparencyAttrib.MDual)
        #self.title.hide()
        self.close=DirectFrame(frameSize=(-32, 0, 0, 32),
                                    frameColor=(1, 1, 1, 1),
                                    frameTexture='icon/close.png',
                                    state=DGG.NORMAL,
                                    parent=pixel2d)        
        self.close.setPos(winX, 0, -32)
        self.close.setBin('fixed', 1)
        self.close.bind(DGG.B1PRESS, self.exit) 
        
        self.start=DirectFrame(frameSize=(-256, 0, 0, 32),                                    
                                    frameTexture='icon/level_select.png',  
                                    frameColor=(1, 1, 1, 1),                                    
                                    parent=pixel2d)       
        self.start.setPos(128+winX/2, 0, -164)
        self.start.setTransparency(TransparencyAttrib.MDual)
        #self.start.bind(DGG.B1PRESS, self.onStart)
        self.start.setBin('fixed', 1)
        #self.start.hide()
        self.start_main=DirectFrame(frameSize=(-192, 0, 0, 32),
                                    frameColor=(1,1,1, 0),    
                                    text_font=self.font,
                                    text='Start in Level 1',
                                    text_pos = (-160, 12,0),
                                    text_scale = 16,
                                    text_fg=(0,0,0,1),
                                    text_align=TextNode.ALeft, 
                                    textMayChange=1,  
                                    state=DGG.NORMAL,
                                    parent=pixel2d)       
        self.start_main.setPos(96+winX/2, 0, -164)
        self.start_main.setTransparency(TransparencyAttrib.MDual)
        self.start_main.bind(DGG.B1PRESS, self.onStart)
        self.start_main.bind(DGG.WITHIN, self.GUIOnEnter, ["4A"]) 
        self.start_main.bind(DGG.WITHOUT, self.GUIOnExit)
        self.start_main.setBin('fixed', 1)
        self.start_main.wrtReparentTo(self.start)
        
        self.start_back=DirectFrame(frameSize=(-32, 0, 0, 32),
                                    frameColor=(1,0,0, 0),                                    
                                    state=DGG.NORMAL,
                                    parent=pixel2d)       
        self.start_back.setPos(128+winX/2, 0, -164)
        self.start_back.setTransparency(TransparencyAttrib.MDual)
        self.start_back.bind(DGG.B1PRESS, self.selectLevel, [1])
        self.start_back.bind(DGG.WITHIN, self.GUIOnEnter, ["4B"]) 
        self.start_back.bind(DGG.WITHOUT, self.GUIOnExit)
        self.start_back.setBin('fixed', 1)
        self.start_back.wrtReparentTo(self.start)
        
        self.start_next=DirectFrame(frameSize=(-32, 0, 0, 32),
                                    frameColor=(0,1,0, 0),                                    
                                    state=DGG.NORMAL,
                                    parent=pixel2d)       
        
        self.start_next.setPos(-96+winX/2, 0, -164)
        self.start_next.setTransparency(TransparencyAttrib.MDual)
        self.start_next.bind(DGG.B1PRESS, self.selectLevel, [-1])
        self.start_next.bind(DGG.WITHIN, self.GUIOnEnter, ["4C"]) 
        self.start_next.bind(DGG.WITHOUT, self.GUIOnExit)
        self.start_next.setBin('fixed', 1)
        self.start_next.wrtReparentTo(self.start)
        
        self.start.hide() 
        
        
       
        self.slider3 = DirectSlider(range=(0,100),
                                    value=50,
                                    pageSize=10,      
                                    thumb_relief=DGG.FLAT,
                                    thumb_frameTexture='glass1.png',
                                    #thumb_frameColor=(1,1,1, 1),
                                    frameTexture='glass2.png',
                                    scale=96,
                                    #frameSize=(-100, 0, 0, 100),
                                    command=self.set_slider,
                                    extraArgs=["3"],
                                    parent=pixel2d)  
        self.slider3.setPos(winX/2, 0, -16)
        self.slider3.setBin('fixed', 2)
        
        self.slider2 = DirectSlider(range=(0,100),
                                    value=50,
                                    pageSize=10,      
                                    thumb_relief=DGG.FLAT,
                                    thumb_frameTexture='glass1.png',
                                    #thumb_frameColor=(1,1,1, 1),
                                    frameTexture='glass2.png',
                                    scale=96,
                                    #frameSize=(-100, 0, 0, 100),
                                    command=self.set_slider,
                                    extraArgs=["2"],
                                    parent=pixel2d)  
        self.slider2.setPos(winX/2, 0, -64)
        self.slider2.setBin('fixed', 2)
        
        self.slider1 = DirectSlider(range=(0,100),
                                    value=50,
                                    pageSize=10,      
                                    thumb_relief=DGG.FLAT,
                                    thumb_frameTexture='glass1.png',
                                    #thumb_frameColor=(1,1,1, 1),
                                    frameTexture='glass2.png',
                                    scale=96,
                                    #frameSize=(-100, 0, 0, 100),
                                    command=self.set_slider,
                                    extraArgs=["1"],
                                    parent=pixel2d)  
        self.slider1.setPos(winX/2, 0, -112)
        self.slider1.setBin('fixed', 2)
        self.slider1.hide()
        self.slider2.hide()
        self.slider3.hide()
        
        self.cursor=DirectFrame(frameSize=(-32, 0, 0, 32),
                                    frameColor=(1, 1, 1, 1),
                                    frameTexture='icon/cursor1.png',
                                    parent=pixel2d)        
        self.cursor.setPos(32,0, -32)
        self.cursor.flattenLight()
        self.cursor.setBin('fixed', 10)
        self.cursor.setTransparency(TransparencyAttrib.MDual)
        
        self.button1A=DirectFrame(frameSize=(-32, 0, 0, 32),
                                    frameColor=(1, 1, 1, 1),
                                    frameTexture='icon/armor.png',
                                    state=DGG.NORMAL,
                                    parent=pixel2d)        
        self.button1A.setPos(128+winX/2, 0, -128)
        self.button1A.setBin('fixed', 1)
        
        self.button1B=DirectFrame(frameSize=(-32, 0, 0, 32),
                                    frameColor=(1, 1, 1, 1),
                                    frameTexture='icon/armor.png',
                                    state=DGG.NORMAL,
                                    parent=pixel2d)        
        self.button1B.setPos(-96+winX/2, 0, -128)
        self.button1B.setBin('fixed', 1)
        
        self.button2A=DirectFrame(frameSize=(-32, 0, 0, 32),
                                    frameColor=(1, 1, 1, 1),
                                    frameTexture='icon/armor.png',
                                    state=DGG.NORMAL,
                                    parent=pixel2d)        
        self.button2A.setPos(128+winX/2, 0, -79)
        self.button2A.setBin('fixed', 1)
        
        self.button2B=DirectFrame(frameSize=(-32, 0, 0, 32),
                                    frameColor=(1, 1, 1, 1),
                                    frameTexture='icon/armor.png',
                                    state=DGG.NORMAL,
                                    parent=pixel2d)        
        self.button2B.setPos(-96+winX/2, 0, -79)
        self.button2B.setBin('fixed', 1)
        
        self.button3A=DirectFrame(frameSize=(-32, 0, 0, 32),
                                    frameColor=(1, 1, 1, 1),
                                    frameTexture='icon/armor.png',
                                    state=DGG.NORMAL,
                                    parent=pixel2d)        
        self.button3A.setPos(128+winX/2, 0, -32)
        self.button3A.setBin('fixed', 1)
        
        self.button3B=DirectFrame(frameSize=(-32, 0, 0, 32),
                                    frameColor=(1, 1, 1, 1),
                                    frameTexture='icon/armor.png',
                                    state=DGG.NORMAL,
                                    parent=pixel2d)        
        self.button3B.setPos(-96+winX/2, 0, -32)
        self.button3B.setBin('fixed', 1)
        
        self.button1A.hide()
        self.button1B.hide()
        self.button2A.hide()
        self.button2B.hide()
        self.button3A.hide()
        self.button3B.hide()
        self.button1A.bind(DGG.WITHIN, self.GUIOnEnter, ["1A"]) 
        self.button1A.bind(DGG.WITHOUT, self.GUIOnExit)
        self.button2A.bind(DGG.WITHIN, self.GUIOnEnter, ["2A"]) 
        self.button2A.bind(DGG.WITHOUT, self.GUIOnExit)
        self.button3A.bind(DGG.WITHIN, self.GUIOnEnter, ["3A"]) 
        self.button3A.bind(DGG.WITHOUT, self.GUIOnExit)
        self.button1B.bind(DGG.WITHIN, self.GUIOnEnter, ["1B"]) 
        self.button1B.bind(DGG.WITHOUT, self.GUIOnExit)
        self.button2B.bind(DGG.WITHIN, self.GUIOnEnter, ["2B"]) 
        self.button2B.bind(DGG.WITHOUT, self.GUIOnExit)
        self.button3B.bind(DGG.WITHIN, self.GUIOnEnter, ["3B"]) 
        self.button3B.bind(DGG.WITHOUT, self.GUIOnExit)
        
        #tooltip
        
        #self.font.setPixelsPerUnit(16)
        #self.font.setMinfilter(Texture.FTNearest )
        #self.font.setMagfilter(Texture.FTNearest )
        #self.font.setAnisotropicDegree(4)        
        #self.font.setNativeAntialias(False) 
        #self.font.setPageSize(1024,1024)
        
        self.Tooltip=DirectLabel(frameColor=(0, 0, 0, 0),
                                text_font=self.font,
                                text='Lorem ipsum dolor sit amet,\n consectetur adipisicing elit,\n sed do eiusmod tempor incididunt \nut labore et dolore magna aliqua.',
                                #pos = (0, 0,-35),
                                text_scale = 16,
                                text_fg=(1,1,1,1),                                
                                text_align=TextNode.ALeft , 
                                textMayChange=1,
                                parent=pixel2d
                                )
        self.Tooltip.flattenLight()                        
        self.Tooltip.setBin('fixed', 300)
        self.Tooltip.hide()
        
        self.tooltip_text=[None, 
                           {"1A":"ARMOR:\nYou have more Hit Points\n",
                           "1B":"REGENERATION:\nYou heal over time\n",
                           "2A":"BLOCK:\nYour block is more effective\n",
                           "2B":"SPEED:\nYour move faster\n",
                           "3A":"DAMAGE:\nYou deal more damage\n",
                           "3B":"CRITICAL HIT:\nChance for a critical hit\n"},
                          {"1A":"BLAST:\nBigger Magic Bolt explosion\n",
                           "1B":"DAMAGE:\nMagic Bolt deals more damage\n",
                           "2A":"LIGHTNING:\nMore damage to far targets\n",
                           "2B":"THUNDER:\nMore damage to near targets\n",
                           "3A":"RAPID CHARGE:\nExponential damage increase\n",
                           "3B":"STATIC CHARGE:\nLinear damage increase\n"},                           
                          {"1A":"BARBS:\nOne hit counts as two\n",
                           "1B":"PIERCE:\nArrows pass through targets\n",
                           "2A":"BLEED:\nDamage over time\n",
                           "2B":"CRIPPLE:\nSlow down enemies\n",
                           "3A":"FINESSE:\nMore critical hits\n",
                           "3B":"PROWESS:\nMore damage\n"},                           
                          {"1A":"BURNING DEATH:\nMagma deals more damage\n",
                           "1B":"MAGMA FLOW:\nMore magma at once\n",
                           "2A":"HEART OF FIRE:\nMagma lasts longer\n",
                           "2B":"VOLCANIC ACTIVITY:\nMagma is bigger\n",
                           "3A":"PHASESHIFT:\nYou can teleport more often\n",
                           "3B":"WARP FIELD:\nFaster recovery after teleport\n"} ]
        #collisions
        #self.traverser=CollisionTraverser("playerTrav")
        #self.traverser.setRespectPrevTransform(True)        
        #self.queue = CollisionHandlerQueue() 
        self.MousePickerNode = CollisionNode('mouseRay')        
        self.pickerNP = base.camera.attachNewNode(self.MousePickerNode)        
        self.MousePickerNode.setFromCollideMask(BitMask32.bit(1))
        self.MousePickerNode.setIntoCollideMask(BitMask32.allOff())
        self.pickerRay = CollisionSegment()               #Make our ray
        self.MousePickerNode.addSolid(self.pickerRay)      #Add it to the collision node        
        self.common['traverser'].addCollider(self.pickerNP, self.common['queue'])
        
        self.accept("mouse1", self.onClick)
        
        taskMgr.doMethodLater(0.2, self.flicker,'flicker')
        #taskMgr.add(self.camera_spin, "camera_spin")  
        taskMgr.add(self.__getMousePos, "chargenMousePos")  
        
        self.current_class=None
        
        self.camLoop=Sequence(LerpHprInterval(self.cameraNode, 10.0, VBase3(-20,0, 0), bakeInStart=0),LerpHprInterval(self.cameraNode, 10.0, VBase3(20,0, 0),bakeInStart=0))
        self.camLoop.loop()
        self.accept( 'window-event', self.windowEventHandler)
    
    def selectLevel(self, next, event=None):
        self.currentLevel+=next
        if self.currentLevel<0:
            self.currentLevel=0
        if self.currentLevel>self.common['max_level']:
            self.currentLevel=self.common['max_level']
        self.start_main['text']="Start in Level "+str(self.currentLevel+1)    
    
    def moveArrow(self, task):
        if self.movingArrow:
            self.arrowTime+=task.time
            if self.arrowTime>3.0:
                self.movingArrow.removeNode()
                self.arrowTime=0.0
                return task.done
            dt = globalClock.getDt()    
            self.movingArrow.setX(self.movingArrow, 400*dt)    
            return task.again
        else:
            return task.done
            
    def fireArrow(self):
        self.movingArrow=loader.loadModel('models/arrow')        
        self.movingArrow.reparentTo(self.arrow_bone)
        self.movingArrow.setP(-45)
        self.movingArrow.wrtReparentTo(render)
        self.arrow.hide()
        self.fireSound.play()
        taskMgr.add(self.moveArrow, "moveArrowTask") 
        Sequence(Wait(0.5),Func(self.arrow.show)).start()
        
    def onStart(self, event=None):
        #unload stuff        
        self.camLoop.pause()
        self.camLoop=None
        base.camera.reparentTo(render)
        self.campmap.removeNode()
        self.node.removeNode()
        self.fire.remove_loop()
        if taskMgr.hasTaskNamed('flicker'):
            taskMgr.remove('flicker') 
        if taskMgr.hasTaskNamed('chargenMousePos'):
            taskMgr.remove('chargenMousePos')  
        self.common['traverser'].removeCollider(self.pickerNP)
        self.pickerNP.removeNode() 
        self.Ambient.removeNode()
                
        self.button1A.destroy()
        self.button1B.destroy()
        self.button2A.destroy()
        self.button2B.destroy()
        self.button3A.destroy()
        self.button3B.destroy()
        self.Tooltip.destroy()
        self.cursor.destroy()
        self.slider1.destroy()
        self.slider2.destroy()
        self.slider3.destroy()
        self.start.destroy()
        self.start_back.destroy()
        self.start_next.destroy()
        self.close.destroy()
        self.title.destroy()
        self.mp_logo.destroy()
        
        render.setLightOff()
        self.ignoreAll()
        
        #self.common['music'].stop()
        
        #self.common['spawner']=Spawner(self.common)
        #self.common['levelLoader']=LevelLoader(self.common)
        
        self.common['levelLoader'].load(self.currentLevel, PCLoad=False)
        #render.ls()
        if self.current_class=="1":
            self.common['PC']=PC1(self.common)
            #self.common['PC'].node.setPos(-12, 0, 0)
        elif self.current_class=="2": 
            self.common['PC']=PC2(self.common)
            #self.common['PC'].node.setPos(-12, 0, 0)
        elif self.current_class=="3": 
            self.common['PC']=PC3(self.common)
            #self.common['PC'].node.setPos(-12, 0, 0)    
        elif self.current_class=="4": 
            self.common['PC']=PC4(self.common)
            #self.common['PC'].node.setPos(-12, 0, 0)
        pos=(data.levels[self.currentLevel]["enter"][0], data.levels[self.currentLevel]["enter"][1], data.levels[self.currentLevel]["enter"][2])     
        self.common['PC'].node.setPos(pos)
        self.common['music'].loop(1, fadeIn=True)
        
    def open_www(self, url, event=None):
        webbrowser.open_new(url)
    
    def windowEventHandler( self, window=None ): 
        #print "resize"
        if window is not None: # window is none if panda3d is not started
            wp = base.win.getProperties()
            X= wp.getXSize()/2
            Y= wp.getYSize()
            self.slider3.setPos(X, 0, -16)
            self.slider2.setPos(X, 0, -64)
            self.slider1.setPos(X, 0, -112)
            self.button1A.setPos(128+X, 0, -128)
            self.button1B.setPos(-96+X, 0, -128)
            self.button2A.setPos(128+X, 0, -79)
            self.button2B.setPos(-96+X, 0, -79)
            self.button3A.setPos(128+X, 0, -32)
            self.button3B.setPos(-96+X, 0, -32)
            self.start.setPos(128+X, 0, -164)
            self.title.setPos(256+X, 0, -128)
            self.close.setPos(X*2, 0, -32)
            self.mp_logo.setPos(256+X, 0, -Y) 
            
    def getSliderValue(self, option):        
        value=0        
        if option[0]=="1":
            value=int(self.slider1['value'])
        elif option[0]=="2":
            value=int(self.slider2['value'])
        elif option[0]=="3":
            value=int(self.slider3['value'])
            
        if self.current_class=="2":    
            if option=="1A":
                return "{0}% blast size".format(value+50)
            elif option=="1B":
                return "{0}% damage".format(75+(101-value)/2)
            elif option=="2A":
                return "{0}% damage to far targets".format(value*2)
            elif option=="2B":
                return "{0}% damage to near targets\n".format(2*(100-value))
            elif option=="3A":
                return "{0}-{1} Lightning damage\n{2}-{3} Magic Bolt damage".format(
                                                                                    int(round(value/100.0+8*(101-value)/100.0)),
                                                                                    int(round(15*value/100.0+8*(101-value)/100)),
                                                                                    2*int(round(2*value/100.0+6*(101-value)/100.0)),
                                                                                    2*int(round(26*value/100.0+20*(101-value)/100))
                                                                                    )
            elif option=="3B":
                return "{0}-{1} Lightning damage\n{2}-{3} Magic Bolt damage".format(
                                                                                    int(round(value/100.0+8*(101-value)/100.0)),
                                                                                    int(round(15*value/100.0+8*(101-value)/100)),
                                                                                    2*int(round(2*value/100.0+6*(101-value)/100.0)),
                                                                                    2*int(round(26*value/100.0+20*(101-value)/100))
                                                                                    )
        elif self.current_class=="1":    
            if option=="1A":
                return "{0} total HP".format(value+50)
            elif option=="1B":
                return "+{0}HP/second".format(round((101-value)/100.0, 1))
            elif option=="2A":
                return "{0}% damage blocked".format(50+(value+1)/2)
            elif option=="2B":
                return "{0}% movement speed".format(75+(101-value)/2)
            elif option=="3A":
                return "{0}-{1} damage".format( int(round(1.0+(value+1.0)/100.0)), int(round(15.0*(1.0+(value+1.0)/50.0))))
            elif option=="3B":
                return "{0}% chance for +{1} damage".format(5+(101-value)/2,5+(101-value)/5)
                
        elif self.current_class=="3":    
            if option=="1A":
                return "{0}% chance to activate".format(int(value/2))
            elif option=="1B":
                return "{0}%chance to pierce".format(int((100-value)/2))
            elif option=="2A":
                return "{0}% of critical hits".format(int(value))
            elif option=="2B":
                return "{0}% of critical hits".format(int(100-value))
            elif option=="3A":
                return "{0}% chance for critical hit".format(25+ int(value/2))
            elif option=="3B":
                return "{0}% damage".format(50+int(100-value))   
        elif self.current_class=="4":    
            if option=="1A":
                return "{0}% damage".format(50+int(value))
            elif option=="1B":
                v=1+int((100-value)/20)
                if v<2:
                    return "Control 1 orb of magma"                    
                return "Control {0} orbs of magma".format(v)
            elif option=="2A":
                return "{0}% time".format(50+int(value))
            elif option=="2B":
                return "{0}% size".format(50+int(100-value))
            elif option=="3A":
                return "Teleport every {0} seconds".format(16.0*((100-value)/1000.0)+0.8)
            elif option=="3B":
                return "{0}% recovery time".format(50+int(value))
                
        return "???"
        
    def GUIOnEnter(self, object, event=None):       
        if object[0]=="4":            
            if object[1]=="A":
                self.Tooltip['text']="Click to start!"    
            elif object[1]=="B":
                self.Tooltip['text']="Next level"        
            elif object[1]=="C":
                self.Tooltip['text']="Previous level"        
            self.Tooltip['text_pos'] = (10, -40,0)
            self.Tooltip['text_align'] =TextNode.ACenter 
            self.Tooltip.show()    
            return
        if not self.current_class:
            return            
        #print int(self.current_class)
        self.Tooltip['text']=self.tooltip_text[int(self.current_class)][object]+self.getSliderValue(object)    
        if object[1]=="A":            
            self.Tooltip['text_pos'] = (30, -10,0)
            self.Tooltip['text_align'] =TextNode.ALeft
        else:            
            self.Tooltip['text_pos'] = (-20, -10,0)
            self.Tooltip['text_align'] =TextNode.ARight
        self.Tooltip.show()
        #print "in"
        
    def GUIOnExit(self, event=None):
        self.Tooltip.hide()
        #print "out"
        
    def start_lightning(self, time=0.03):
        taskMgr.doMethodLater(time, self.lightning,'vfx')
        self.magicSound.play()
        
    def lightning(self, task):
        self.char2_magic.show()
        self.vfxU=self.vfxU+0.5   
        if self.vfxU>=1.0:
            self.vfxU=0
            self.vfxV=self.vfxV-0.125
        if self.vfxV <=-1:
            self.char2_magic.hide()
            self.vfxU=0
            self.vfxV=0
            return task.done
        self.char2_magic.setTexOffset(TextureStage.getDefault(), self.vfxU, self.vfxV)
        return task.again   
        
    def loopAnim(self, actor, anim):
        actor.loop(anim)
    
    def set_slider(self, id):
        #self.current_class=id
        #print id, 
        if id=="1":
            self.common['pc_stat1']=int(self.slider1['value'])
            #print self.common['pc_stat1']
        elif id=="2":
            self.common['pc_stat2']=int(self.slider2['value'])
            #print self.common['pc_stat2']
        elif id=="3":
            self.common['pc_stat3']=int(self.slider3['value'])        
            #print self.common['pc_stat3']
            
    def onClick(self):
        self.common['traverser'].traverse(render) 
        my_class=None
        for entry in self.common['queue'].getEntries():
            if entry.getIntoNodePath().hasTag("class"):
                my_class=entry.getIntoNodePath().getTag("class")
                
        if my_class=="1":
            self.slider1['value']=50        
            self.slider2['value']=50        
            self.slider3['value']=50
            self.current_class=my_class
            self.title.hide()
            self.start.show()
            self.button1A.show()
            self.button1B.show()
            self.button2A.show()
            self.button2B.show()
            self.button3A.show()
            self.button3B.show()
            
            self.button1A['frameTexture']='icon/armor.png'
            self.button1B['frameTexture']='icon/heart.png'
            self.button2A['frameTexture']='icon/shield2.png'
            self.button2B['frameTexture']='icon/move.png'
            self.button3A['frameTexture']='icon/power.png'
            self.button3B['frameTexture']='icon/critical.png'
            
            #self.skills.show()
            self.slider1.show()
            self.slider2.show()
            self.slider3.show()            
            Sequence(self.character1.actorInterval("attack"),self.character1.actorInterval("block"), Func(self.loopAnim, self.character1, "idle")).start()
            self.swingSound.play()
            #self.character1.play("attack")
            self.character2.loop("idle")
        elif my_class=="2":
            self.slider1['value']=50        
            self.slider2['value']=50        
            self.slider3['value']=50
            self.current_class=my_class
            self.title.hide()
            self.start.show()
            self.button1A.show()
            self.button1B.show()
            self.button2A.show()
            self.button2B.show()
            self.button3A.show()
            self.button3B.show()
            
            self.button1A['frameTexture']='icon/blast.png'
            self.button1B['frameTexture']='icon/damage.png'
            self.button2A['frameTexture']='icon/lightning.png'
            self.button2B['frameTexture']='icon/thunder.png'
            self.button3A['frameTexture']='icon/amp.png'
            self.button3B['frameTexture']='icon/volt.png'
            
            
            self.slider1.show()
            self.slider2.show()
            self.slider3.show()                
            Sequence(self.character2.actorInterval("attack", playRate=0.8),Func(self.loopAnim, self.character2, "idle")).start()
            Sequence(Wait(0.3), Func(self.start_lightning, 0.05)).start()
            #self.character2.play("attack")
            self.character1.loop("idle")
            #RayVfx(self.character2, texture='vfx/lightning.png').start()
        elif my_class=="3":
            self.slider1['value']=50        
            self.slider2['value']=50        
            self.slider3['value']=50
            self.current_class=my_class
            self.title.hide()
            self.start.show()
            self.button1A.show()
            self.button1B.show()
            self.button2A.show()
            self.button2B.show()
            self.button3A.show()
            self.button3B.show()
            
            self.button1A['frameTexture']='icon/barbs.png'
            self.button1B['frameTexture']='icon/pierce.png'
            self.button2A['frameTexture']='icon/bleed.png'
            self.button2B['frameTexture']='icon/cripple.png'
            self.button3A['frameTexture']='icon/finese.png'
            self.button3B['frameTexture']='icon/bow_damage.png'
            
            
            self.slider1.show()
            self.slider2.show()
            self.slider3.show()
            self.drawSound.play()
            self.character3.play("attack")
            Sequence(Wait(1.5),Func(self.fireArrow), Func(self.character3.play, "reset"),Wait(1.0),Func(self.loopAnim, self.character3, "idle")).start()
        elif my_class=="4":
            self.slider1['value']=50        
            self.slider2['value']=50        
            self.slider3['value']=50
            self.current_class=my_class
            self.title.hide()
            self.start.show()
            self.button1A.show()
            self.button1B.show()
            self.button2A.show()
            self.button2B.show()
            self.button3A.show()
            self.button3B.show()
            
            self.button1A['frameTexture']='icon/hand_o_fate.png'
            self.button1B['frameTexture']='icon/magma_flow.png'
            self.button2A['frameTexture']='icon/heart_o_fire.png'
            self.button2B['frameTexture']='icon/vulcanic.png'
            self.button3A['frameTexture']='icon/warp.png'
            self.button3B['frameTexture']='icon/thorns.png'
            
            #self.skills.show()
            self.slider1.show()
            self.slider2.show()
            self.slider3.show()
            self.character4.loop("attack")
            aura=vfx(self.character4, texture='vfx/tele2.png',scale=.5, Z=.85, depthTest=False, depthWrite=False)
            aura.show()
            aura.start()
            self.FFSound.play()
            Sequence(Wait(2.2), Func(self.loopAnim, self.character4, "idle")).start()
               
    def exit(self, event=None):
        self.common['root'].save_and_exit()
        #sys.exit()
    
    def __getMousePos(self, task):
        if base.mouseWatcherNode.hasMouse():  
            mpos = base.mouseWatcherNode.getMouse()
            self.pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())        
            pos2d=Point3(mpos.getX() ,0, mpos.getY())
            self.cursor.setPos(pixel2d.getRelativePoint(render2d, pos2d)) 
            self.Tooltip.setPos(self.cursor.getPos())    
        return task.again  
        
    def flicker(self, task):
        self.pLight.setAttenuation(Point3(1, 0, random.uniform(.1, 0.15)))  
        self.pLightNode.setZ(random.uniform(.9, 1.1))
        #self.pLight.setColor(VBase4(random.uniform(.9, 1.0), random.uniform(.9, 1.0), .9, 1))        
        return task.again  
        
    def camera_spin(self, task):
        H=self.cameraNode.getH()
        #Z=self.cameraNode.getZ()
        #print H
        if H<=-20.0 or H>=20.0:
            if self.reverse_spin:
                self.reverse_spin=False
            else:
                self.reverse_spin=True
        if self.reverse_spin:        
            self.cameraNode.setH(self.cameraNode, 4*globalClock.getDt())
            #self.cameraNode.setZ(Z+0.1*globalClock.getDt())
        else:
            self.cameraNode.setH(self.cameraNode, -4*globalClock.getDt())
            #self.cameraNode.setZ(Z-0.1*globalClock.getDt())
        return task.again  
#c=Camp()
#run()        