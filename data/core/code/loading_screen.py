'''Avolition 2.0
INFO:
    This file provides the loading context manager. 
    It will show a loading screen while thing are being loaded.
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

from contextlib import contextmanager
from panda3d.core import *
from direct.gui.OnscreenImage import OnscreenImage

@contextmanager
def loading(*args):
    x=base.win.get_x_size()//2
    y=base.win.get_y_size()//2
    img=loader.load_texture('ui/loading.png')
    scale=(256, 0, 256)#img size//2
    if ConfigVariableBool('framebuffer-srgb').getValue():
        tex_format=img.get_format()
        if tex_format == Texture.F_rgb:
            tex_format = Texture.F_srgb
        elif tex_format == Texture.F_rgba:
            tex_format = Texture.F_srgb_alpha
        img.set_format(tex_format)
    load_screen = OnscreenImage(image = img, scale=scale, pos = (x, 0, -y), parent=pixel2d)
    #render 3 frames because we may be in a threaded rendering pipeline
    #we render frames to make sure the load screen is shown
    base.graphicsEngine.renderFrame()
    base.graphicsEngine.renderFrame()
    base.graphicsEngine.renderFrame()
    try:
        yield
    finally:
        #render a few frames and fade out the loading screen
        for i in range(30):
            base.graphicsEngine.renderFrame()
            color=1.0-i/30.0
            load_screen.set_color(color,color,color)
        load_screen.remove_node()
