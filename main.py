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

from panda3d.core import loadPrcFileData
loadPrcFileData('','multisamples 2') 
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
    print "No config file, using default"
loadPrcFileData('','show-frame-rate-meter  #f') 
#loadPrcFileData('','win-origin -2 -2')
from panda3d.core import ConfigVariableInt
from panda3d.core import ConfigVariableBool
from panda3d.core import ConfigVariableString  
config_aa=ConfigVariableInt('multisamples', 0)
config_fulscreen=ConfigVariableBool('fullscreen')
config_win_size=ConfigVariableInt('win-size', '640 480') 
config_bloom=ConfigVariableBool('bloom', 1)
config_safemode=ConfigVariableBool('safemode', 0)
config_music=ConfigVariableInt('music-volume', '30') 
config_sfx=ConfigVariableInt('sound-volume', '100') 
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

from panda3d.core import WindowProperties
wp = WindowProperties.getDefault() 
wp.setFixedSize(True)  
wp.setCursorHidden(False)
wp.setFullscreen(False)
wp.setUndecorated(True)  
wp.setTitle("Avolition - Configuration")   
wp.setSize(512,512)
wp.setOrigin(-2,-2)
WindowProperties.setDefault(wp)
from direct.gui.DirectGui import *
from panda3d.core import *
import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
import sys
#import collections


class Config(DirectObject):
    def __init__(self):
        base.setBackgroundColor(0, 0, 0)
        base.exitFunc = self.save_and_exit
        self.background = DirectFrame(frameSize=(-512, 0, 0, 512),
                                    frameColor=(1,1,1, 1),
                                    frameTexture='config2.png',
                                    parent=pixel2d)        
        self.background.setPos(512, 0, -512)
        self.background.flattenLight()
        self.background.setTransparency(TransparencyAttrib.MDual)
        self.background.setBin('fixed', 10)
        
        self.close=DirectFrame(frameSize=(-16, 0, 0, 16),
                                    frameColor=(1,1,1, 0),
                                    state=DGG.NORMAL,
                                    parent=pixel2d)
        self.close.setBin('fixed', 11)                                        
        self.close.setPos(508, 0, -19)
        self.close.bind(DGG.B1PRESS, sys.exit)
        
        self.fullscreen=DirectFrame(frameSize=(-160, 0, 0, 32),
                                    frameColor=(0,0,0, 1),
                                    state=DGG.NORMAL,
                                    parent=self.background)
        self.fullscreen.setPos(198, 0, -160)
        self.fullscreen.setBin('fixed', 1)
        self.fullscreen.bind(DGG.B1PRESS, self.set_option, ["window", False])
        
        self.windowed=DirectFrame(frameSize=(-160, 0, 0, 32),
                                    frameColor=(0,0,0, 1),
                                    state=DGG.NORMAL,
                                    parent=self.background)
        self.windowed.setPos(496, 0, -160)
        self.windowed.setBin('fixed', 1)
        self.windowed.bind(DGG.B1PRESS, self.set_option, ["window", True])
        
        self.res11=DirectFrame(frameSize=(-160, 0, 0, 32),
                                    frameColor=(0,0,0, 1),
                                    state=DGG.NORMAL,
                                    parent=self.background)
        self.res11.setPos(160, 0, -192)
        self.res11.setBin('fixed', 1)
        self.res11.bind(DGG.B1PRESS, self.set_option, ["resolution", "800 600"])
        
        
        self.res21=DirectFrame(frameSize=(-160, 0, 0, 32),
                                    frameColor=(0,0,0, 1),
                                    state=DGG.NORMAL,
                                    parent=self.background)
        self.res21.setPos(160, 0, -224)
        self.res21.setBin('fixed', 1)
        self.res21.bind(DGG.B1PRESS, self.set_option, ["resolution", "1280 800"])
        
        
        self.res31=DirectFrame(frameSize=(-160, 0, 0, 32),
                                    frameColor=(0,0,0, 1),
                                    state=DGG.NORMAL,
                                    parent=self.background)
        self.res31.setPos(160, 0, -256)
        self.res31.setBin('fixed', 1)
        self.res31.bind(DGG.B1PRESS, self.set_option, ["resolution", "1280 720"])
        
        
        
        self.res12=DirectFrame(frameSize=(-165, 0, 0, 32),
                                    frameColor=(0,0,0, 1),
                                    state=DGG.NORMAL,
                                    parent=self.background)
        self.res12.setPos(332, 0, -192)
        self.res12.setBin('fixed', 1)
        self.res12.bind(DGG.B1PRESS, self.set_option, ["resolution", "1024 768"])
        
        
        self.res22=DirectFrame(frameSize=(-165, 0, 0, 32),
                                    frameColor=(0,0,0, 1),
                                    state=DGG.NORMAL,
                                    parent=self.background)
        self.res22.setPos(332, 0, -224)
        self.res22.setBin('fixed', 1)
        self.res22.bind(DGG.B1PRESS, self.set_option, ["resolution", "1440 900"])
        
        
        self.res32=DirectFrame(frameSize=(-165, 0, 0, 32),
                                    frameColor=(0,0,0, 1),
                                    state=DGG.NORMAL,
                                    parent=self.background)
        self.res32.setPos(332, 0, -256)
        self.res32.setBin('fixed', 1)
        self.res32.bind(DGG.B1PRESS, self.set_option, ["resolution", "1366 768"])
        
        
        self.res13=DirectFrame(frameSize=(-170, 0, 0, 32),
                                    frameColor=(0,0,0, 1),
                                    state=DGG.NORMAL,
                                    parent=self.background)
        self.res13.setPos(510, 0, -192)
        self.res13.setBin('fixed', 1)
        self.res13.bind(DGG.B1PRESS, self.set_option, ["resolution", "1280 1024"])
        
        
        self.res23=DirectFrame(frameSize=(-170, 0, 0, 32),
                                    frameColor=(0,0,0, 1),
                                    state=DGG.NORMAL,
                                    parent=self.background)
        self.res23.setPos(510, 0, -224)
        self.res23.setBin('fixed', 1)
        self.res23.bind(DGG.B1PRESS, self.set_option, ["resolution", "1680 1050"])
        
        self.res33=DirectFrame(frameSize=(-170, 0, 0, 32),
                                    frameColor=(0,0,0, 1),
                                    state=DGG.NORMAL,
                                    parent=self.background)
        self.res33.setPos(510, 0, -256)
        self.res33.setBin('fixed', 1)
        self.res33.bind(DGG.B1PRESS, self.set_option, ["resolution", "1920 1080"])
        
        self.bloom=DirectFrame(frameSize=(-140, 0, 0, 32),
                                    frameColor=(0,0,0, 1),
                                    state=DGG.NORMAL,
                                    parent=self.background)
        self.bloom.setPos(186, 0, -288)
        self.bloom.setBin('fixed', 1)
        self.bloom.bind(DGG.B1PRESS, self.set_option, ["bloom", True])
        
        self.no_bloom=DirectFrame(frameSize=(-180, 0, 0, 32),
                                    frameColor=(0,0,0, 1),
                                    state=DGG.NORMAL,
                                    parent=self.background)
        self.no_bloom.setPos(472, 0, -288)
        self.no_bloom.setBin('fixed', 1)
        self.no_bloom.bind(DGG.B1PRESS, self.set_option, ["bloom", False]) 
        
        self.aa=DirectFrame(frameSize=(-190, 0, 0, 32),
                                    frameColor=(0,0,0, 1),
                                    state=DGG.NORMAL,
                                    parent=self.background)
        self.aa.setPos(206, 0, -320)
        self.aa.setBin('fixed', 1)
        self.aa.bind(DGG.B1PRESS, self.set_option, ["aa", True]) 
        
        self.no_aa=DirectFrame(frameSize=(-250, 0, 0, 32),
                                    frameColor=(0,0,0, 1),
                                    state=DGG.NORMAL,
                                    parent=self.background)
        self.no_aa.setPos(502, 0, -320)
        self.no_aa.setBin('fixed', 1)
        self.no_aa.bind(DGG.B1PRESS, self.set_option, ["aa", False]) 
        
        self.safeModeButton=DirectFrame(frameSize=(-270, 0, 0, 32),
                                    frameColor=(0,0,0, 1),
                                    state=DGG.NORMAL,
                                    parent=self.background)
        self.safeModeButton.setPos(392, 0, -352)
        self.safeModeButton.setBin('fixed', 1)
        self.safeModeButton.bind(DGG.B1PRESS, self.set_option, ["safemode", False])
        
        
        self.save=DirectFrame(frameSize=(-220, 0, 0, 32),
                                    frameColor=(0,0,0, 1),
                                    #frameTexture='glass.png',
                                    state=DGG.NORMAL,
                                    parent=self.background)
        self.save.setPos(366, 0, -512)
        self.save.setBin('fixed', 1)
        self.save.bind(DGG.B1PRESS, self.save_and_run) 
        
        self.audio_slider = DirectSlider(range=(0,100),
                                    value=config_sfx.getValue(),
                                    pageSize=10,
                                    scale=0.55,
                                    pos=(0.4,0,-0.68),
                                    thumb_relief=DGG.FLAT,
                                    thumb_frameTexture='glass3.png',
                                    frameTexture='glass2.png',
                                    command=self.set_option,extraArgs=["audio"])
                                    
        self.music_slider = DirectSlider(range=(0,100),
                                    value=config_music.getValue(),
                                    pageSize=10,
                                    scale=0.55,
                                    pos=(0.4,0,-0.77),
                                    thumb_relief=DGG.FLAT,
                                    thumb_frameTexture='glass3.png',
                                    frameTexture='glass2.png',
                                    command=self.set_option, extraArgs=["music"])                            
        
        self.options={}
        if(config_aa.getValue()>0):   
            self.set_option("aa", True)
        else:    
            self.set_option("aa", False)
            
        if config_bloom.getValue():   
            self.set_option("bloom", True)
        else:    
            self.set_option("bloom", False)         
        if config_fulscreen.getValue():   
            self.set_option("window", False)
        else:    
            self.set_option("window", True)
        if config_safemode.getValue():
            self.options['safemode']=True
            self.safeModeButton['frameColor']=(1,1,1, 1)
            self.safeModeButton['frameTexture']='glass.png'
        else:    
            self.options['safemode']=False
        self.set_option("resolution", str(config_win_size.getWord(0))+" "+str(config_win_size.getWord(1)))    
        #keyboard setup:
        self.font = loader.loadFont('Bitter-Bold.otf')
        self.font.setPixelsPerUnit(16)
        self.font.setMinfilter(Texture.FTNearest )
        self.font.setMagfilter(Texture.FTNearest )
        #self.font.setAnisotropicDegree(4)        
        self.font.setNativeAntialias(False) 
        self.font.setPageSize(1024,1024)
        
        self.key_background = DirectFrame(frameSize=(-512, 0, 0, 512),
                                    frameColor=(1,1,1, 1),
                                    frameTexture='config_keys.png',
                                    parent=pixel2d)        
        self.key_background.setPos(512, 0, -512)
        self.key_background.flattenLight()
        self.key_background.setTransparency(TransparencyAttrib.MDual)
        self.key_background.setBin('fixed', 10)
        self.key_background.hide()
        
        self.press = DirectFrame(frameSize=(-512, 0, 0, 512),
                                    frameColor=(1,1,1, 1),
                                    frameTexture='config_press.png',
                                    parent=pixel2d)        
        self.press.setPos(512, 0, -512)
        self.press.flattenLight()
        self.press.setTransparency(TransparencyAttrib.MDual)
        self.press.setBin('fixed', 10)
        self.press.hide()
        
        self.back_press=DirectFrame(frameSize=(-220, 0, 0, 32),
                                    frameColor=(1,1,1, 1),
                                    frameTexture='glass.png',
                                    state=DGG.NORMAL,
                                    parent=self.press)
        self.back_press.setPos(366, 0, -512)
        self.back_press.setBin('fixed', 1)
        self.back_press.bind(DGG.B1PRESS, self.cancelKey)
        
        
        
        self.back=DirectFrame(frameSize=(-220, 0, 0, 32),
                                    frameColor=(1,1,1, 1),
                                    frameTexture='glass.png',
                                    state=DGG.NORMAL,
                                    parent=self.key_background)
        self.back.setPos(366, 0, -512)
        self.back.setBin('fixed', 1)
        self.back.bind(DGG.B1PRESS, self.keySetup, [False])
        
        
        self.keys=DirectFrame(frameSize=(-350, 0, 0, 30),
                                    frameColor=(1,1,1,1),
                                    frameTexture='glass3.png',
                                    state=DGG.NORMAL,
                                    parent=self.background)
        self.keys.setPos(430, 0, -383)
        self.keys.setBin('fixed', 1)
        self.keys.bind(DGG.B1PRESS, self.keySetup, [True])
        
        #self.keymap=collections.OrderedDict()
        self.keymap={}
        self.keymap['key_forward']=config_forward.getValue().split('|')
        self.keymap['key_back']=config_back.getValue().split('|')
        self.keymap['key_left']=config_left.getValue().split('|')
        self.keymap['key_right']=config_right.getValue().split('|')
        self.keymap['key_cam_left']=config_camera_left.getValue().split('|')
        self.keymap['key_cam_right']=config_camera_right.getValue().split('|')
        self.keymap['key_action1']=config_action1.getValue().split('|')
        self.keymap['key_action2']=config_action2.getValue().split('|')
        self.keymap['key_zoomin']=config_zoomin.getValue().split('|')
        self.keymap['key_zoomout']=config_zoomout.getValue().split('|')
        
        self.keymapOrder=['key_forward','key_back', 'key_left', 'key_right', 'key_cam_left', 'key_cam_right', 'key_action1', 'key_action2', 'key_zoomin', 'key_zoomout']
        
        self.isListeningForKeys=False
        self.currentKey=None
        self.currentButton=None
        x=0
        for key in self.keymapOrder:
            self.keymap[key].append(DirectFrame(frameSize=(-140, 0, 0, 32),
                                    text_font=self.font,
                                    frameColor=(1,1,1, 1),
                                    frameTexture='glass.png',
                                    text=self.keymap[key][0].upper(),
                                    text_scale=16,
                                    text_fg=(1,1,1,1),
                                    state=DGG.NORMAL,
                                    text_pos=(-70,13),
                                    text_align=TextNode.ACenter,
                                    parent=self.key_background))
            self.keymap[key][2].setPos(355, 0, -160+x)
            self.keymap[key][2].setBin('fixed', 1)
            self.keymap[key][2].bind(DGG.B1PRESS, self.listenForKey, [key, 2])
            self.keymap[key].append(DirectFrame(frameSize=(-140, 0, 0, 32),
                                    text_font=self.font,
                                    frameColor=(1,1,1, 1),
                                    frameTexture='glass.png',
                                    text=self.keymap[key][1].upper(),
                                    text_scale=16,
                                    text_fg=(1,1,1,1),
                                    state=DGG.NORMAL,
                                    text_pos=(-70,13),
                                    text_align=TextNode.ACenter,
                                    parent=self.key_background))
            self.keymap[key][3].setPos(507, 0, -160+x)
            self.keymap[key][3].setBin('fixed', 1)
            self.keymap[key][3].bind(DGG.B1PRESS, self.listenForKey, [key, 3])
            x+=-32
        
        base.buttonThrowers[0].node().setButtonDownEvent('buttonDown')
        self.accept('buttonDown', self.getKey)
    
    def listenForKey(self, key, button, event=None):
        self.currentKey=key
        self.currentButton=button
        self.isListeningForKeys=True
        self.key_background.hide()
        self.press.show()
        
    def keySetup(self, show=True, mouse=None):
        if show:
            self.background.hide()    
            self.music_slider.hide()
            self.audio_slider.hide()
            self.key_background.show()
        else:
            self.background.show()    
            self.music_slider.show()
            self.audio_slider.show()
            self.key_background.hide()
            
    def cancelKey(self, event=None):
        self.isListeningForKeys=False
        self.key_background.show()
        self.press.hide()   
    
    def getKey(self, keyname):
        #print keyname
        if keyname=="control" or keyname=="shift" or keyname=="alt":
            return       
        if self.isListeningForKeys:
            for key in self.keymap:
                if keyname in self.keymap[key]:
                    #print keyname,"used"
                    button=self.keymap[key].index(keyname)
                    #print button
                    old_key=self.keymap[self.currentKey][self.currentButton-2]
                    #print old_key
                    self.keymap[key][button+2]['text']=old_key.upper()
                    self.keymap[key][button]=old_key                    
                    break
                    #return
            #print keyname    
            self.isListeningForKeys=False
            self.key_background.show()
            self.press.hide()
            self.keymap[self.currentKey][self.currentButton]['text']=keyname.upper()
            self.keymap[self.currentKey][self.currentButton-2]=keyname
            
    def set_option(self, option, value=None, mouse=None):
        if option=="safemode":
            if not self.options[option]:
                self.safeModeButton['frameColor']=(1,1,1, 1)
                self.safeModeButton['frameTexture']='glass.png'
                self.options[option]=True
            else:
                self.safeModeButton['frameColor']=(0,0,0, 1)
                self.options[option]=False
                print "off!"
        elif option =="music":
            value=int(self.music_slider['value'])
        elif option =="audio":
            value=int(self.audio_slider['value'])            
        elif option == "window":
            if value==True:
                self.fullscreen['frameColor']=(0,0,0, 1)
                self.windowed['frameColor']=(1,1,1, 1)
                self.windowed['frameTexture']='glass.png'
            else:
                self.windowed['frameColor']=(0,0,0, 1)
                self.fullscreen['frameColor']=(1,1,1, 1)
                self.fullscreen['frameTexture']='glass.png'
        elif option == "resolution":
            if value=="800 600":
                self.res11['frameColor']=(1,1,1, 1)
                self.res11['frameTexture']='glass.png'
                self.res12['frameColor']=(0,0,0, 1)
                self.res13['frameColor']=(0,0,0, 1)
                self.res21['frameColor']=(0,0,0, 1)
                self.res22['frameColor']=(0,0,0, 1)
                self.res23['frameColor']=(0,0,0, 1)
                self.res31['frameColor']=(0,0,0, 1)
                self.res32['frameColor']=(0,0,0, 1)
                self.res33['frameColor']=(0,0,0, 1)
            if value=="1024 768":
                self.res12['frameColor']=(1,1,1, 1)
                self.res12['frameTexture']='glass.png'
                self.res11['frameColor']=(0,0,0, 1)
                self.res13['frameColor']=(0,0,0, 1)
                self.res21['frameColor']=(0,0,0, 1)
                self.res22['frameColor']=(0,0,0, 1)
                self.res23['frameColor']=(0,0,0, 1)
                self.res31['frameColor']=(0,0,0, 1)
                self.res32['frameColor']=(0,0,0, 1)
                self.res33['frameColor']=(0,0,0, 1)
            if value=="1280 1024":
                self.res13['frameColor']=(1,1,1, 1)
                self.res13['frameTexture']='glass.png'
                self.res11['frameColor']=(0,0,0, 1)
                self.res12['frameColor']=(0,0,0, 1)
                self.res21['frameColor']=(0,0,0, 1)
                self.res22['frameColor']=(0,0,0, 1)
                self.res23['frameColor']=(0,0,0, 1)
                self.res31['frameColor']=(0,0,0, 1)
                self.res32['frameColor']=(0,0,0, 1)
                self.res33['frameColor']=(0,0,0, 1)
            if value=="1280 800":
                self.res21['frameColor']=(1,1,1, 1)
                self.res21['frameTexture']='glass.png'
                self.res12['frameColor']=(0,0,0, 1)
                self.res13['frameColor']=(0,0,0, 1)
                self.res11['frameColor']=(0,0,0, 1)
                self.res22['frameColor']=(0,0,0, 1)
                self.res23['frameColor']=(0,0,0, 1)
                self.res31['frameColor']=(0,0,0, 1)
                self.res32['frameColor']=(0,0,0, 1)
                self.res33['frameColor']=(0,0,0, 1)
            if value=="1440 900":
                self.res22['frameColor']=(1,1,1, 1)
                self.res22['frameTexture']='glass.png'
                self.res12['frameColor']=(0,0,0, 1)
                self.res13['frameColor']=(0,0,0, 1)
                self.res21['frameColor']=(0,0,0, 1)
                self.res11['frameColor']=(0,0,0, 1)
                self.res23['frameColor']=(0,0,0, 1)
                self.res31['frameColor']=(0,0,0, 1)
                self.res32['frameColor']=(0,0,0, 1)
                self.res33['frameColor']=(0,0,0, 1)
            if value=="1680 1050":
                self.res23['frameColor']=(1,1,1, 1)
                self.res23['frameTexture']='glass.png'
                self.res12['frameColor']=(0,0,0, 1)
                self.res13['frameColor']=(0,0,0, 1)
                self.res21['frameColor']=(0,0,0, 1)
                self.res22['frameColor']=(0,0,0, 1)
                self.res11['frameColor']=(0,0,0, 1)
                self.res31['frameColor']=(0,0,0, 1)
                self.res32['frameColor']=(0,0,0, 1)
                self.res33['frameColor']=(0,0,0, 1)
            if value=="1280 720":
                self.res31['frameColor']=(1,1,1, 1)
                self.res31['frameTexture']='glass.png'
                self.res12['frameColor']=(0,0,0, 1)
                self.res13['frameColor']=(0,0,0, 1)
                self.res21['frameColor']=(0,0,0, 1)
                self.res22['frameColor']=(0,0,0, 1)
                self.res23['frameColor']=(0,0,0, 1)
                self.res11['frameColor']=(0,0,0, 1)
                self.res32['frameColor']=(0,0,0, 1)
                self.res33['frameColor']=(0,0,0, 1)
            if value=="1366 768":
                self.res32['frameColor']=(1,1,1, 1)
                self.res32['frameTexture']='glass.png'
                self.res12['frameColor']=(0,0,0, 1)
                self.res13['frameColor']=(0,0,0, 1)
                self.res21['frameColor']=(0,0,0, 1)
                self.res22['frameColor']=(0,0,0, 1)
                self.res23['frameColor']=(0,0,0, 1)
                self.res31['frameColor']=(0,0,0, 1)
                self.res11['frameColor']=(0,0,0, 1)
                self.res33['frameColor']=(0,0,0, 1)
            if value=="1920 1080":                
                self.res33['frameColor']=(1,1,1, 1)
                self.res33['frameTexture']='glass.png'
                self.res12['frameColor']=(0,0,0, 1)
                self.res13['frameColor']=(0,0,0, 1)
                self.res21['frameColor']=(0,0,0, 1)
                self.res22['frameColor']=(0,0,0, 1)
                self.res23['frameColor']=(0,0,0, 1)
                self.res31['frameColor']=(0,0,0, 1)
                self.res32['frameColor']=(0,0,0, 1)
                self.res11['frameColor']=(0,0,0, 1)
        elif option == "bloom":
            if value==False:
                self.bloom['frameColor']=(0,0,0, 1)
                self.no_bloom['frameColor']=(1,1,1, 1)
                self.no_bloom['frameTexture']='glass.png'
            else:
                self.no_bloom['frameColor']=(0,0,0, 1)
                self.bloom['frameColor']=(1,1,1, 1)
                self.bloom['frameTexture']='glass.png'
        elif option == "aa":
            if value==False:
                self.aa['frameColor']=(0,0,0, 1)
                self.no_aa['frameColor']=(1,1,1, 1)
                self.no_aa['frameTexture']='glass.png'
            else:
                self.no_aa['frameColor']=(0,0,0, 1)
                self.aa['frameColor']=(1,1,1, 1)
                self.aa['frameTexture']='glass.png'
        #print option, value
        self.options[option]=value
    def clean_up(self):
        self.res33.destroy()
        self.res33.destroy()
        self.res12.destroy()
        self.res13.destroy()
        self.res21.destroy()
        self.res22.destroy()
        self.res23.destroy()
        self.res31.destroy()
        self.res32.destroy()
        self.res11.destroy()
        self.bloom.destroy()
        self.no_bloom.destroy()
        self.aa.destroy()
        self.no_aa.destroy()
        self.fullscreen.destroy()
        self.windowed.destroy()
        #self.background.destroy()
        self.save.destroy()
        self.audio_slider.destroy()
        self.music_slider.destroy()
        self.key_background.destroy()
        self.press.destroy()
        self.back_press.destroy()
        self.keys.destroy()
        self.close.destroy()
        for key in self.keymap:
            self.keymap[key][2].destroy()
            self.keymap[key][3].destroy()
            
        
        #self.options=None
        #self.keymap=None
        self.isListeningForKeys=None
        self.currentKey=None
        self.currentButton=None
        self.ignoreAll()
        
    def save_and_run(self, mouse=None):
        with open(path+"autoconfig.txt", "w") as temp:
            temp.write("#auto generated config file\n")
            temp.write("#use config.txt to hand-edit custom options\n")
            temp.write("win-size "+str(self.options["resolution"])+"\n")
            temp.write("music-volume "+str(self.options["music"])+"\n")
            temp.write("sound-volume "+str(self.options["audio"])+"\n")
            if self.options["bloom"]:
                temp.write("bloom 1\n")
            else:    
                temp.write("bloom 0\n")
            if self.options["aa"]:
                temp.write("multisamples 2\n")
            else:
                temp.write("multisamples 0\n")
            if self.options["window"]:
                temp.write("fullscreen 0\n")    
            else:    
                temp.write("fullscreen 1\n") 
            if self.options["safemode"]:
                temp.write("safemode 1\n")    
            else:    
                temp.write("safemode 0\n")     
            for key in self.keymap:
                temp.write(key+" "+self.keymap[key][0]+"|"+self.keymap[key][1]+"\n") 
                
        self.background['frameTexture']="loading2.png"
        #print self.options
        #sys.exit()
        #base.openMainWindow()
        #base.exitfunc( )
        #print "I'm out"
        self.clean_up()
        from game import Game        
        game=Game(self.background, self)
        

    def save_and_exit(self, event=None):
        print "exit"
        #base.closeWindow(base.win)
        with open(path+"autoconfig.txt", "w") as temp:
            temp.write("#auto generated config file\n")
            temp.write("#use config.txt to hand-edit custom options\n")
            temp.write("win-size "+str(self.options["resolution"])+"\n")
            temp.write("music-volume "+str(int(base.musicManager.getVolume()*100.0))+"\n")
            temp.write("sound-volume "+str(int(base.sfxManagerList[0].getVolume()*100.0))+"\n")
            if self.options["bloom"]:
                temp.write("bloom 1\n")
            else:    
                temp.write("bloom 0\n")
            if self.options["aa"]:
                temp.write("multisamples 2\n")
            else:
                temp.write("multisamples 0\n")
            if self.options["window"]:
                temp.write("fullscreen 0\n")    
            else:    
                temp.write("fullscreen 1\n") 
            if self.options["safemode"]:
                temp.write("safemode 1\n")    
            else:    
                temp.write("safemode 0\n")     
            for key in self.keymap:
                temp.write(key+" "+self.keymap[key][0]+"|"+self.keymap[key][1]+"\n")         
        sys.exit()
main = Config()    
run()      