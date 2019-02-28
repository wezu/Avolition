'''Avolition 2.0
INFO:
    This module handles music and sound playback. 
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
from direct.interval.MetaInterval import Sequence
from direct.interval.FunctionInterval import Func, Wait

__all__ = ['Audio']

class Audio(object):
    def __init__(self, drop_off_factor=0.0, distance_factor=0.3):
        """This module handles music and sound playback."""
        self.music_manager=base.musicManager
        self.sound_manager=base.sfxManagerList[0]

        self.sound_manager.audio3dSetDropOffFactor(drop_off_factor)
        self.sound_manager.audio3dSetDistanceFactor(distance_factor)

        self.sfx=[]
        self.sounds={}
        self.current_music=None
        self.playlists={}
        self.current_track= None
        
        taskMgr.add(self.update, 'audio_update_tsk')

    def load_sounds(self, sound_dict, positional=True):
        """Preload sounds for later playback"""
        for name, filename in sound_dict.items():
            self.sounds[name]=loader.load_sound(self.sound_manager, filename, positional)

    def set_music_volume(self, value):
        """Sets the music volume in 0.0-1.0 range"""
        self.music_manager.set_volume(value)
        Config.set('audio','music-volume', str(value))

    def set_sound_volume(self, value):
        """Sets the sound volume in 0.0-1.0 range"""
        self.sound_manager.set_volume(value)
        Config.set('audio','sound-volume', str(value))

    def next_track(self):
        """Jumps to the next music track(or the first if there is no next track)"""
        if self.current_track is None:
            return
        self.current_track+=1
        if self.current_track >= len(self.playlists[self.current_playlist]):
            self.current_track=0
        self.current_music=self.playlists[self.current_playlist][self.current_track]
        self.track_seq=Sequence(Wait(self.current_music.length()), Func(self.next_track))
        self.track_seq.start()
        self.current_music.play()
        
    def load_music(self, track_names, playlist_name='default'):
        """
        Loads music tracks from the track_names list
        """
        if playlist_name not in self.playlists:
            self.playlists[playlist_name]=[]        
        for track_name in track_names:
            self.playlists[playlist_name].append(loader.load_music(track_name))

        self.current_music=self.playlists[playlist_name][0]
        self.current_track=0
        self.current_playlist=playlist_name
    
    
    def play_music(self, playlist=None):
        """
        Starts playing music 
        """
        if playlist:
            self.current_playlist=playlist    
        self.track_seq=Sequence(Wait(self.current_music.length()), Func(self.next_track))
        self.track_seq.start()
        self.current_music.play()

    def stop_music(self):
        """Stops the music"""
        self.current_music.stop()
        self.current_track = None

    def stop_sound(self, sound):
        """Stops a sound"""
        sound.stop()

    def is_playing(self, sound):
        if sound is None:
            return False
        return sound.status() == sound.PLAYING
	
    def play_sound(self, sound, node=None, loop=False, pos=Vec3(0,0,0), vel=Vec3(0,0,0), rate=1.0):
        """
        Play a positional (3D) sound at node or pos location.
        If node is not None the sound will move with the node.
        """
        #print('playing ', sound, node)
        if sound in self.sounds:
            sfx=self.sounds[sound]
        else:
            sfx=loader.load_sound(self.sound_manager, sound, True)
            self.sounds[sound]=sfx
        if node is not None:
            pos=node.get_pos(render)
        sfx.set3dAttributes(*pos, *vel)
        if loop:
            sfx.set_loop_count(0)
        sfx.set_play_rate(rate)
        sfx.play()
        self.sfx.append((sfx, node))
        return sfx

    def play_sound_2d(self, sound):
        """Plays the sound """
        if sound in self.sounds:
            sfx=self.sounds(sound)
        else:
            sfx=loader.load_sound(self.sound_manager, sound, False)
            self.sounds[sound]=sfx
        sfx.play()
        self.sfx.append((sfx, None))
        return sfx

    def stop_all(self):
        """ Stops all currently playing sound effects (but not music!)"""
        for sfx, node in self.sfx:
            sfx.stop()

    def update(self, task):
        """Updates the position and velocity of currently playing sounds"""
        dt=globalClock.getDt()
        pos=base.camera.get_pos(render)
        forward=render.get_relative_vector(base.camera, Vec3.forward())
        up=render.get_relative_vector(base.camera, Vec3.up())
        vel=base.camera.get_pos_delta(render)/dt
        self.sound_manager.audio3dSetListenerAttributes(*pos, *vel, *forward, *up)

        for i, (sfx, node) in enumerate(self.sfx):
            if sfx.status()==sfx.PLAYING:
                if node is not None:
                    if node.is_empty():
                        sfx.stop()
                        #print('removing', self.sfx[i])
                        del self.sfx[i]
                    else:
                        pos=node.get_pos(render)
                        vel=node.get_pos_delta(render)/dt
                        sfx.set3dAttributes(*pos, *vel)
            else:
                #print('removing', self.sfx[i])
                del self.sfx[i]
        return task.cont
