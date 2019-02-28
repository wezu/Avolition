'''Avolition 2.0
INFO:
    This module is the Game Master (Dungeon Maater). It controls monster spawn,
    level progresion, win/lose conditions.  
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
class GameMaster:
    def __init__(self):
        self.levels=[
                   {"map_name":"models/level2.bam",      
                   "map_monsters":[10, 11, 12,13, 14, 15, 16,16],
                   "num_monsters":3,
                   "kills_for_key":12,
                   "enter":[-3,0,0],
                   "exit":[54.5,-11,0]},
                   
                   {"map_name":"models/level1.bam",      
                   "map_monsters":[10, 11, 12,13],
                   "num_monsters":5,
                   "kills_for_key":15,
                   "enter":[0,-2.0,0],
                   "exit":[-10,-24,0]},
                   
                   {"map_name":"models/level3.bam",      
                   "map_monsters":[15, 14, 16, 16, 2],
                   "num_monsters":4,
                   "kills_for_key":18,
                   "enter":[2,0,0],
                   "exit":[-40,34,0]}, 
                   
                   {"map_name":"models/level4.bam",      
                   "map_monsters":[13,15, 16, 2,6],
                   "num_monsters":4,
                   "kills_for_key":18,
                   "enter":[0,2.5,0],
                   "exit":[-14.5,-21,0]}, 
                   
                   {"map_name":"models/level5.bam",      
                   "map_monsters":[13, 16, 10, 6, 7, 2],
                   "num_monsters":3,
                   "kills_for_key":20,
                   "enter":[-3,0,0],
                   "exit":[40,2,0]},
                   
                   {"map_name":"models/level_a1.bam",      
                   "map_monsters":[2,2,6,6,7,16],
                   "num_monsters":4,
                   "kills_for_key":25,
                   "enter":[-0.3,-30.5,0],
                   "exit":[-33,0,0]},       
                   
                   {"map_name":"models/level_a2.bam",      
                   "map_monsters":[3,6,7, 8],
                   "num_monsters":3,
                   "kills_for_key":25,
                   "enter":[2,-21,0],
                   "exit":[-23,-43,0]},
                   
                   {"map_name":"models/level_a3.bam",      
                   "map_monsters":[2,3,3,4,4],
                   "num_monsters":4,
                   "kills_for_key":25,
                   "enter":[0,1,0],
                   "exit":[30,43,0]},
                   
                   {"map_name":"models/level_a4.bam",      
                   "map_monsters":[2,3,4,4,9],
                   "num_monsters":4,
                   "kills_for_key":25,
                   "enter":[0,-3,0],
                   "exit":[-33,23,0]},
                   
                   {"map_name":"models/level_a5.bam",      
                   "map_monsters":[3,4,5,9],
                   "num_monsters":4,
                   "kills_for_key":25,
                   "enter":[-0.5,0.0,0],
                   "exit":[30.25,64,0]},
                   
                   {"map_name":"models/level_b1.bam",      
                   "map_monsters":[1,1,2,9],
                   "num_monsters":3,
                   "kills_for_key":25,
                   "enter":[0.0,3.0,0],
                   "exit":[-10,-64.5,0]},
                   
                   {"map_name":"models/level_b2.bam",      
                   "map_monsters":[1,1,1,2,3,4,8,9],
                   "num_monsters":4,
                   "kills_for_key":25,
                   "enter":[0.0,12.0,0],
                   "exit":[0,-54.5,0]},
                   
                   {"map_name":"models/level_b3.bam",      
                   "map_monsters":[1,1,2,3,4,5,5,6,7],
                   "num_monsters":4,
                   "kills_for_key":25,
                   "enter":[0.0,1.5,0],
                   "exit":[-5.5,20,0]},
                   
                   {"map_name":"models/level_b4.bam",      
                   "map_monsters":[1,1,1,1,2,2,3,4,5,5,5,6,7,8,9,9,10,11,12,13,14,15, 16],
                   "num_monsters":5,
                   "kills_for_key":30,
                   "enter":[0.0,1.0,0],
                   "exit":[0,-54.5,0]},
                   
                   {"map_name":"models/end_level.bam",      
                   "map_monsters":[0],
                   "num_monsters":0,
                   "kills_for_key":20,
                   "enter":[0.0,0.0,0],
                   "exit":[100,100,0]},
                   ]
        self.monsters={
                        'goblin':
                        {
                        "model":"models/npc/m_goblin",
                        "root_bone":"Bip01 Spine2",
                        "anim":{"walk":"models/npc/a_goblin_walk","attack":"models/npc/a_goblin_attack","die":"models/npc/a_goblin_die"},
                        "speed":1.0,
                        "scale":0.09,
                        "heading":0,
                        "hit_vfx":'vfx/blood_red.png',
                        "hit_sfx":'hit2',
                        "die_sfx":'die7',
                        "arrowhit_sfx":'hit_arrow',
                        "attack_sfx":'m_attack1',
                        "attack_pattern":[.4],
                        "hp":90,
                        "armor":0,
                        "dmg":5        
                        },
                        'metal_golem':
                        {
                        "model":"models/npc/m_golem_metal",
                        "root_bone":"body",
                        "anim":{"walk":"models/npc/a_golem1_walk","attack":"models/npc/a_golem1_attack","die":"models/npc/a_golem1_die"},
                        "speed":2.2,
                        "scale":0.14,
                        "heading":180,
                        "hit_vfx":'vfx/sparks.png',
                        "hit_sfx":'hit_metal',
                        "die_sfx":'die_metal',
                        "arrowhit_sfx":'hit_arrow_metal',
                        "attack_sfx":'m_attack1',
                        "attack_pattern":[.3,.4,.2],
                        "hp":130,
                        "armor":5,
                        "dmg":3
                        },
                        'gold_golem':
                        {                        
                        "model":"models/npc/m_golem_gold",
                        "root_bone":"Bip001 Spine1",
                        "anim":{"walk":"models/npc/a_golem2_walk","attack":"models/npc/a_golem2_attack","die":"models/npc/a_golem2_die"},
                        "speed":1.35,
                        "scale":0.38,
                        "heading":180,
                        "hit_vfx":'vfx/sparks.png',
                        "hit_sfx":'hit3',
                        "die_sfx":'die4',
                        "arrowhit_sfx":'hit_arrow_rock',
                        "attack_sfx":'m_attack1',
                        "attack_pattern":[.3],
                        "hp":100,
                        "armor":2,
                        "dmg":6
                        },
                        'lava_golem':
                        {
                        "model":"models/npc/m_golem_lava1",
                        "root_bone":"Bip001 Spine1",
                        "anim":{"walk":"models/npc/a_golem2_walk","attack":"models/npc/a_golem2_attack","die":"models/npc/a_golem2_die"},
                        "speed":1.2,
                        "scale":0.38,
                        "heading":180,
                        "hit_vfx":'vfx/sparks.png',
                        "hit_sfx":'hit1',
                        "die_sfx":'die3',
                        "arrowhit_sfx":'hit_arrow_rock',
                        "attack_sfx":'m_attack1',
                        "attack_pattern":[.3],
                        "hp":150,
                        "armor":3,
                        "dmg":8
                        },
                        'magma_golem':
                        {
                        "model":"models/npc/m_golem_lava2",
                        "root_bone":"Bip001 Spine1",
                        "anim":{"walk":"models/npc/a_golem2_walk","attack":"models/npc/a_golem2_attack","die":"models/npc/a_golem2_die"},
                        "speed":.95,
                        "scale":0.39,
                        "heading":180,
                        "hit_vfx":'vfx/sparks.png',
                        "hit_sfx":'hit1',
                        "die_sfx":'die1',
                        "arrowhit_sfx":'hit_arrow_rock',
                        "attack_sfx":'m_attack1',
                        "attack_pattern":[.3],
                        "hp":140,
                        "armor":1,
                        "dmg":7
                        },
                        'magic_golem':
                        {
                        "model":"models/npc/m_golem_magic",
                        "root_bone":"Bip001 Spine1",
                        "anim":{"walk":"models/npc/a_golem2_walk","attack":"models/npc/a_golem2_attack","die":"models/npc/a_golem2_die"},
                        "speed":1.1,
                        "scale":0.38,
                        "heading":180,
                        "hit_vfx":'vfx/sparks.png',
                        "hit_sfx":'hit1',
                        "die_sfx":'die6',
                        "arrowhit_sfx":'hit_arrow_rock',
                        "attack_sfx":'m_attack1',
                        "attack_pattern":[.3],
                        "hp":175,
                        "armor":5,
                        "dmg":9
                        },
                        'rock_golem':
                        {
                        "model":"models/npc/m_golem_rock1",
                        "root_bone":"Bip001 Spine1",
                        "anim":{"walk":"models/npc/a_golem2_walk","attack":"models/npc/a_golem2_attack","die":"models/npc/a_golem2_die"},
                        "speed":1.0,
                        "scale":0.38,
                        "heading":180,
                        "hit_vfx":'vfx/sparks.png',
                        "hit_sfx":'hit1',
                        "die_sfx":'die3',
                        "arrowhit_sfx":'hit_arrow_rock',
                        "attack_sfx":'m_attack1',
                        "attack_pattern":[.3],
                        "hp":120,
                        "armor":2,
                        "dmg":10
                        },
                        'stone_golem':
                        {
                        "model":"models/npc/m_golem_rock2",
                        "root_bone":"Bip001 Spine1",
                        "anim":{"walk":"models/npc/a_golem2_walk","attack":"models/npc/a_golem2_attack","die":"models/npc/a_golem2_die"},
                        "speed":0.95,
                        "scale":0.39,
                        "heading":180,
                        "hit_vfx":'vfx/sparks.png',
                        "hit_sfx":'hit1',
                        "die_sfx":'die3',
                        "arrowhit_sfx":'hit_arrow_rock',
                        "attack_sfx":'m_attack1',
                        "attack_pattern":[.3],
                        "hp":130,
                        "armor":3,
                        "dmg":8
                        },
                        'paskuda':#do not want
                        {
                        "model":"models/npc/m_monster1",        
                        "root_bone":"Bip001 Spine",
                        "anim":{"walk":"models/npc/a_monster1_walk","attack":"models/npc/a_monster1_attack","die":"models/npc/a_monster1_die"},
                        "speed":1.0,
                        "scale":0.24,
                        "heading":180,
                        "hit_vfx":'vfx/blood_red.png',
                        "hit_sfx":'hit2',
                        "die_sfx":'die5',
                        "arrowhit_sfx":'hit_arrow',
                        "attack_sfx":'m_attack1',
                        "attack_pattern":[1.0, .3],
                        "hp":100,
                        "armor":0,
                        "dmg":4
                        },
                        'laguna_monster':#do nat want(?)
                        {
                        "model":"models/npc/m_monster2",              
                        "root_bone":"Bip001 Spine1",
                        "anim":{"walk":"models/npc/a_monster2_walk","attack":"models/npc/a_monster2_attack","die":"models/npc/a_monster2_die"},
                        "speed":1.1,
                        "scale":0.27,
                        "heading":180,
                        "hit_vfx":'vfx/blood_green.png',
                        "hit_sfx":'hit1',
                        "die_sfx":'die6',
                        "arrowhit_sfx":'hit_arrow',
                        "attack_sfx":'m_attack1',
                        "attack_pattern":[.5],
                        "hp":200,
                        "armor":0,
                        "dmg":11
                        },
                        'zombie_nopants':
                        {
                        "model":"models/npc/m_zombie1",           
                        "root_bone":"Bip001 Spine1",
                        "anim":{"walk":"models/npc/a_zombie_walk1","attack":"models/npc/a_zombie_attack","die":"models/npc/a_zombie_die"},
                        "speed":1.0,
                        "scale":0.024,
                        "heading":180,
                        "hit_vfx":'vfx/blood_red.png',
                        "hit_sfx":'hit2',
                        "die_sfx":'die1',        
                        "arrowhit_sfx":'hit_arrow',
                        "attack_sfx":'m_attack1',
                        "attack_pattern":[.4],
                        "hp":50,
                        "armor":0,
                        "dmg":5
                        },
                        'zombie_brain':
                        {
                        "model":"models/npc/m_zombie2",        
                        "root_bone":"Bip001 Spine1",
                        "anim":{"walk":"models/npc/a_zombie_walk1","attack":"models/npc/a_zombie_attack","die":"models/npc/a_zombie_die"},
                        "speed":1.0,
                        "scale":0.024,
                        "heading":180,
                        "hit_vfx":'vfx/blood_red.png',
                        "hit_sfx":'hit2',
                        "die_sfx":'die1',
                        "arrowhit_sfx":'hit_arrow',
                        "attack_sfx":'m_attack1',
                        "attack_pattern":[.4],
                        "hp":60,
                        "armor":0,
                        "dmg":6
                        },
                        'zombie_wound':
                        {
                        "model":"models/npc/m_zombie3",        
                        "root_bone":"Bip001 Spine1",
                        "anim":{"walk":"models/npc/a_zombie_walk2","attack":"models/npc/a_zombie_attack","die":"models/npc/a_zombie_die"},
                        "speed":1.1,
                        "scale":0.024,
                        "heading":180,
                        "hit_vfx":'vfx/blood_red.png',
                        "hit_sfx":'hit2',
                        "die_sfx":'die1',
                        "arrowhit_sfx":'hit_arrow',
                        "attack_sfx":'m_attack1',
                        "attack_pattern":[.4],
                        "hp":70,
                        "armor":0,
                        "dmg":7
                        },
                        'zombie_dry':
                        {
                        "model":"models/npc/m_zombie4",        
                        "root_bone":"Bip001 Spine1",
                        "anim":{"walk":"models/npc/a_zombie_walk3","attack":"models/npc/a_zombie_attack","die":"models/npc/a_zombie_die"},
                        "speed":1.0,
                        "scale":0.024,
                        "heading":180,
                        "hit_vfx":'vfx/blood_red.png',
                        "hit_sfx":'hit2',
                        "die_sfx":'die1',
                        "arrowhit_sfx":'hit_arrow',
                        "attack_sfx":'m_attack1',
                        "attack_pattern":[.4],
                        "hp":80,
                        "armor":0,
                        "dmg":7
                        },
                        'zombie_sick'
                        {
                        "model":"models/npc/m_zombie5",        
                        "root_bone":"Bip001 Spine1",
                        "anim":{"walk":"models/npc/a_zombie_walk2","attack":"models/npc/a_zombie_attack","die":"models/npc/a_zombie_die"},
                        "speed":1.0,
                        "scale":0.024,
                        "heading":180,
                        "hit_vfx":'vfx/blood_red.png',
                        "hit_sfx":'hit2',
                        "die_sfx":'die2',
                        "arrowhit_sfx":'hit_arrow',
                        "attack_sfx":'m_attack1',
                        "attack_pattern":[.4],
                        "hp":90,
                        "armor":0,
                        "dmg":8
                        },
                        'zombie_noarm'
                        {
                        "model":"models/npc/m_zombie6",        
                        "root_bone":"Bip001 Spine1",
                        "anim":{"walk":"models/npc/a_zombie_walk3","attack":"models/npc/a_zombie_attack","die":"models/npc/a_zombie_die"},
                        "speed":1.0,
                        "scale":0.024,
                        "heading":180,
                        "hit_vfx":'vfx/blood_red.png',
                        "hit_sfx":'hit2',
                        "die_sfx":'die2',
                        "arrowhit_sfx":'hit_arrow',
                        "attack_sfx":'m_attack1',
                        "attack_pattern":[.4],
                        "hp":100,
                        "armor":0,
                        "dmg":9
                        },
                        'skelington':
                        {
                        "model":"models/npc/m_skel",        
                        "root_bone":"Bip001 Spine2",
                        "anim":{"walk":"models/npc/a_skel_walk","attack":"models/npc/a_skel_attack","die":"models/npc/a_skel_die"},
                        "speed":1.0,
                        "scale":0.1,
                        "heading":180,
                        "hit_vfx":'vfx/sparks.png',
                        "hit_sfx":'hit1',
                        "die_sfx":'die6',
                        "arrowhit_sfx":'hit_arrow_bone',
                        "attack_sfx":'m_attack1',
                        "attack_pattern":[5.2, .5],
                        "hp":110,
                        "armor":2,
                        "dmg":5
                        }
                    }