'''
INFO:
    This module has some helper functions used for pathfinding and level loading
    This module is imported by level.py
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

from panda3d.core import *
from panda3d.egg import *
from panda3d.bullet import *
from direct.showutil.Rope import Rope
from collections import defaultdict, deque
import itertools
import time
import heapq

__all__=[ 'PriorityQueue', 'distance', 'find_edges', 'get_center', 'get_poly', 
        'nearest','smooth_path', 'a_star_search']

class PriorityQueue:
    """Helper class for pathfinding """
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]

#Helper functions for constructing the navgraph and finding paths

def distance(start, end):
    """Line distance from start to end, both need to be VBase3  """
    v=end-start
    return v.length()

def find_edges(verts):
    """
    Given a list of vertex id returns all possible edges
    that the verts can form as a set of (frozen) sets for quick membership tests
    """
    s=set()
    for combo in itertools.combinations(verts, 2):
        s.add(frozenset(combo))
    return s

def get_center(poly):
    """Returns the center of a polygon"""
    num=float(len(poly))
    total=Point3D(0)
    for vert in poly:
        total+=vert
    return Vec3(*(i/num for i in total))

def get_poly(group, polys):
    """
    Adds all polygons from the EggGroup group to the polys dict
    The polys dict have the center of the polygon as key
    and a list of the vert ids as value 
    """
    if isinstance(group, EggGroup):
        for child in group.getChildren():
            get_poly(child, polys)
    elif isinstance(group, EggPolygon):
        verts=[]
        pos=[]
        for vert in group.getVertices():
            verts.append(vert.getIndex())
            pos.append(vert.getPos3())
        polys[get_center(pos)]=verts

def nearest(data, point, threshold=0.76):
    """
    Returns the value nearest the point in the data list
    If threshold is non-zero, the first value threshold away or closer is returned.  
    """
    rounded=Vec3(int(point.x), int(point.y), int(point.z))
    if rounded in data:
        return rounded
    minimal=None
    best=None
    for v in data:
        d=(v-point).length()
        if d < threshold:
            return v
        if minimal is None:
            minimal = d
        if d <= minimal:
            minimal=d
            best=v
    return best

def smooth_path(path, smooth_factor=0.5):
    """Creates a smoother path from a given path (list of points)"""
    if len(path)<4 or smooth_factor <0.01:
        return path
    r=Rope()
    verts=[(None, point) for point in path]
    r.setup(order=4, verts=verts, knots = None)
    return r.getPoints(int(len(path)*smooth_factor))

def a_star_search(start, goal, neighbors, cost, heuristic, max_move=8000):
    """
    A* search algorithm.
    Returns a path (list of points) from start to goal 
    """
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        current = frontier.get()

        if max_move is not None:
            max_move-=1
            if max_move<0:
                return None

        if current == goal:
            break

        for next_neighbor in neighbors[current]:
            new_cost = cost_so_far[current] + cost[current][next_neighbor]
            if next_neighbor not in cost_so_far or new_cost < cost_so_far[next_neighbor]:
                cost_so_far[next_neighbor] = new_cost
                priority = new_cost + heuristic(goal, next_neighbor)
                frontier.put(next_neighbor, priority)
                came_from[next_neighbor] = current
    current = goal
    path = [current]
    while current != start:
        try:
            current = came_from[current]
        except:
            return None
        path.append(current)
    #path.reverse()
    return smooth_path(path, 2.0)

