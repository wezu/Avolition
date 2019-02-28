'''Avolition 2.0
INFO:
    This module makes the player classes available for the game.
    If you want to add new characters, this is the place to add them.
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

from pc_druid import Druid
from pc_witch import Witch
from pc_rogue import Rogue
from pc_gladiator import Gladiator

class Players:
    def __init__(self):
        self.pc={}
        self.pc['witch']=Witch(node=deferred_render.attach_new_node('witch'))
        self.pc['witch'].actor.set_pos(-1,1.7,0)
        self.pc['witch'].actor.set_h(25)

        self.pc['rogue']=Rogue(node=deferred_render.attach_new_node('rogue'))
        self.pc['rogue'].actor.set_pos(-1.8,0.9, -0.02)
        self.pc['rogue'].actor.set_h(40)


        self.pc['gladiator']=Gladiator(node=deferred_render.attach_new_node('gladiator'))
        self.pc['gladiator'].actor.set_pos(1, 2.2, 0)
        self.pc['gladiator'].actor.set_h(-20)

        self.pc['druid']=Druid(node=deferred_render.attach_new_node('druid'))
        self.pc['druid'].actor.set_pos(1.8,0.9, 0)
        self.pc['druid'].actor.set_h(-60)

    def reset(self):
        self.pc['witch'].actor.set_pos(-1,1.7,0)
        self.pc['witch'].actor.set_h(25)

        self.pc['rogue'].actor.set_pos(-1.8,0.9, -0.02)
        self.pc['rogue'].actor.set_h(40)

        self.pc['gladiator'].actor.set_pos(1, 2.2, 0)
        self.pc['gladiator'].actor.set_h(-20)

        self.pc['druid'].actor.set_pos(1.8,0.9, 0)
        self.pc['druid'].actor.set_h(-60)

    def select(self, name):
        for pc_name, pc in self.pc.items():
            if pc_name!=name:
                pc.hide()
            else:
                pc.bind_keys()

    def items(self):
        return self.pc.items()

    def __getitem__(self, item):
        return self.pc[item]

    def __contains__(self, item):
        return item in self.pc
