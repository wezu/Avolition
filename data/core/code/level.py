'''Avolition 2.0
INFO:
    This module is responsible for loading level geometry, collisions, navmesh, cubemap,
    and also plotting paths through the level (pathfinding).
    The pathfinding runs on a separate thread, and returns paths at it's own pace. 
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
from panda3d.egg import *
from panda3d.bullet import *
from direct.showutil.Rope import Rope
from collections import defaultdict, deque
import itertools
import os
import pickle
import threading
import time
import heapq
from pathfind import *

def get_local_file(path):
    return getModelPath().findFile(path).toOsSpecific()

class Level():
    def __init__(self, root):
        self.root=root

        self.plane = game.world_np.attach_new_node(BulletRigidBodyNode('Ground'))
        self.plane.node().add_shape(BulletPlaneShape(Vec3(0, 0, 1), 0))
        self.plane.set_pos(0, 0, 0)
        self.plane.set_collide_mask(game.bit_mask.floor)
        game.world.attach_rigid_body(self.plane.node())
        self.navgraph={'neighbors':None,'cost':None,'heuristic':distance,'max_move':8000}

        self.request_que=deque()
        self.deamon_stop_event= threading.Event()
        self.deamon = threading.Thread(name='daemon', target=self.pathfinder, args=(self.deamon_stop_event,))
        self.deamon.setDaemon(True)
        self.deamon.start()

    def request_path(self, start, goal, target_que):
        """Adds the path from start to goal to the target_que at some later point in time """
        self.request_que.append((start, goal, target_que))

    def _find_path(self, start, goal):
        """ Performs a A* search with start and goal points that can be outside the navgraph"""
        start =nearest(self.navgraph['neighbors'], start)
        goal =nearest(self.navgraph['neighbors'], goal)
        path= a_star_search(start=start, goal=goal, **self.navgraph)
        return path

    def pathfinder(self, stop_event):
        """Path finding deamon """
        while not stop_event.is_set():
            if len (self.request_que) > 0:
                start, goal, target_que=self.request_que.popleft()
                target_que.append(self._find_path(start, goal))
            time.sleep(1.0/60.0)

    def load(self, model, navmesh=None, cubemap=None):
        """
        Loads the model (with collisiin mesh),
        Converts the navmesh to a navgraph,
        Loads the cubmap 
        """
        if cubemap:
            deferred_renderer.set_cubemap(cubemap)
        #load the model
        self.mesh=loader.load_model(model)
        self.mesh.reparent_to(self.root)

        #set material on black parts
        black=self.mesh.find('**/black')
        if black:
            black.set_shader(Shader.load(Shader.SLGLSL, 'shaders/geo_black_v.glsl', 'shaders/geo_black_f.glsl'))
        #hide the top
        top=self.mesh.find('**/top')
        if top:
            top.hide()
        #load collision geometry
        self.body = game.world_np.attach_new_node(BulletRigidBodyNode(model))
        for body in BulletHelper.from_collision_solids(self.mesh, True):
            for shape in body.node().get_shapes():
                shape.set_margin(0.0)
                self.body.node().add_shape(shape)
        self.body.node().set_mass(0)
        self.body.set_collide_mask(game.bit_mask.wall)
        game.world.attach_rigid_body(self.body.node())

        #navgrapth
        if navmesh:
            navmesh=get_local_file(navmesh)
            input_egg = EggData()
            input_egg.read(navmesh)
            #find polygons
            poly={}
            for child in input_egg.getChildren():
                if isinstance(child, EggGroup):
                    get_poly(child, poly)
            #find enges
            edges={}
            for center, p in poly.items():
                edges[center]=find_edges(p)

            #find neighbors
            #.nbr stands for NeighBoRs
            if os.path.exists(navmesh+'.nbr'):
                with open(navmesh+'.nbr', 'rb') as pf:
                    neighbors = pickle.load(pf)
            else:
                neighbors=defaultdict(set)
                for center, edge in edges.items():
                    for other_center, other in edges.items():
                        if edge != other:
                            common= edge.intersection(other)
                            if common:
                                neighbors[center].add(other_center)

                with open(navmesh+'.nbr', 'wb') as pf:
                    pickle.dump(neighbors, pf)

            #find costs
            cost={}
            for start, ends in neighbors.items():
                costs={}
                for end in ends:
                    costs[end]=distance(start, end)
                cost[start]=costs

            self.navgraph['cost']=cost
            self.navgraph['neighbors']=neighbors
