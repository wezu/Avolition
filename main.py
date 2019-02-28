#!/usr/bin/env python3
#import python stuff
import random
import operator
import sys
import os
import builtins
import math
import json
import ast
import copy
import types
import itertools
from importlib import import_module
from collections import deque
from functools import lru_cache
from functools import wraps
from contextlib import contextmanager
from time import perf_counter as timer
import traceback
#import panda3d stuff
from panda3d.core import *
from panda3d.bullet import *
from direct.showbase.DirectObject import DirectObject
from direct.interval import IntervalManager
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.PythonUtil import fitSrcAngle2Dest
from direct.showutil.Rope import Rope
#we need to read the config before we go on
import configparser
Config = configparser.ConfigParser()
Config.read('config.ini')
builtins.Config = Config
#read all options as prc_file_data in case they have p3d meaning
for section in Config.sections():
    for option in Config.options(section):
        loadPrcFileData("", option +' '+Config.get(section, option))
#if this is set to something else things will break, so we overide here!
loadPrcFileData('','textures-power-2 None')
loadPrcFileData('','bullet-filter-algorithm groups-mask')
#loadPrcFileData('','show-buffers 1')

from direct.showbase import ShowBase

##Data loading:##
#add 'code' and 'plugins' dirs to sys.path
#add anything else to modelpath
plugins={}
builtins.plugins=plugins
for mod in reversed(Config.get('datafiles', 'loadorder').split(', ')):
    for directory in os.listdir('data/'+mod):
        if directory in ('code', 'plugins'):
            sys.path.append('data/'+mod+'/'+directory)
        if directory == 'plugins':
            for file_name in os.listdir('data/'+mod+'/'+directory):
                if file_name[-3:]=='.py':
                    try:
                        plugins[file_name[:-3]]=import_module(file_name[:-3]).Plugin()
                    except:
                        print('Error loading plugin:'+'data/'+mod+'/'+directory+'/'+file_name)
        getModelPath().appendDirectory('data/'+mod)

wp = WindowProperties.getDefault()
wp.set_title("Avolition 2.0 by wezu")
try:
    wp.set_cursor_filename('ui/cursor.cur')
    wp.set_icon_filename('ui/icon.ico')
except:
    pass
WindowProperties.setDefault(wp)

from game import Game


screen_text=None
builtins.screen_text = screen_text

def print_to_screen(*args, sep=' ', end=None, file=None, flush=False):
    if builtins.screen_text is not None:
        builtins.screen_text.destroy()
        builtins.screen_text=None
    if args:
        txt=sep.join((str(i) for i in args))+'\nPress [F10] to hide this message'
        builtins.screen_text = OnscreenText(text = txt,
                                        pos = (8,-48),
                                        scale =16,
                                        fg=(1,1.0,1.0,1),
                                        shadow=(0,0,0,1),
                                        wordwrap=64,
                                        align=TextNode.ALeft,
                                        parent=pixel2d)

#builtins.print = print_to_screen
##Start the game ##
class App(DirectObject):
    def __init__(self):
        #init panda3d showbase
        base = ShowBase.ShowBase()

        builtins.print_to_screen=print_to_screen

        base.setBackgroundColor(0, 0, 0)
        base.disableMouse()
        base.win.set_close_request_event('exit-event')
        self.accept('exit-event', self.on_exit)
        self.accept('f10', print_to_screen)

        #hacking the event menager
        #eventMgr.doEvents=self.doEvents
        #hacking interval manager
        #IntervalManager.ivalMgr._step=IntervalManager.ivalMgr.step
        #IntervalManager.ivalMgr.step=self.ivalMgr_step
        #hacking task manager
        #taskMgr._step=taskMgr.step
        #taskMgr.step=self.tsk_step
        self.game=Game(self)
             
        '''try:
            #init game
            self.game=Game(self)
            #start plugins
            for plugin in plugins.values():
                try:
                    plugin.start()
                except:
                    pass
        except Exception as err:
            trbck=traceback.format_exc(limit=2, chain=True)
            txt='Oops, something went wrong!\n\n'+trbck+'\nPlease report this error to the game developers.'
            print_to_screen(txt)'''

    def tsk_step(self):
        try:
            taskMgr._step()
        except:
            trbck=traceback.format_exc(limit=2, chain=False)
            txt='Oops, something went wrong!\n\n'+trbck+'\nPlease report this error to the game developers.'
            print_to_screen(txt)

    def ivalMgr_step(self):
        try:
            IntervalManager.ivalMgr._step()
        except:
            trbck=traceback.format_exc(limit=2, chain=False)
            txt='Oops, something went wrong!\n\n'+trbck+'\nPlease report this error to the game developers.'
            print_to_screen(txt)

    def doEvents(self):
        """
        Process all the events on the C++ event queue
        """
        while (not eventMgr.eventQueue.isQueueEmpty()):
            try:
                eventMgr.processEvent(eventMgr.eventQueue.dequeueEvent())
            except:
                trbck=traceback.format_exc(limit=2, chain=False)
                txt='Oops, something went wrong!\n\n'+trbck+'\nPlease report this error to the game developers.'
                print_to_screen(txt)


    def final_exit(self):
        base.destroy()
        os._exit(1)

    def on_exit(self):
        try:
            self.game.exit_game()
        except:
            self.final_exit()

##Run the show!##
app=App()
base.run()
