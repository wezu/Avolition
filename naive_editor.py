# Nameless A.I. Version E editor
from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
import direct.directbase.DirectStart
from direct.gui.DirectGui import *
import json
from dijkstra2 import Graph
from vis_ninth import VisibilityPolygon
from direct.gui.OnscreenText import OnscreenText
import math

myFile="level4.egg"

# Function to put instructions on the screen.
def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1,1,1,1),
      pos=(-1.3, pos), align=TextNode.ALeft, scale = .05)
 
class AI_level_editor(DirectObject):
    def __init__(self):        
        addInstructions(0.80,"WSAD keys to move the camera")
        addInstructions(0.75,"E R keys to rotate the camera")
        addInstructions(0.70,"Z X keys to zoom the camera")
        addInstructions(0.65,"ENTER saves the map")
        addInstructions(0.60,"Mouse-1 to draw a wall or spawnpoint")
        addInstructions(0.55,"Space to switch between walls and spawnpoints")
        addInstructions(0.50,"Tab to switch wall mode")
        addInstructions(0.45,"Esc to remove last wall/spawnpoint")
        
        #pointer
        self.pointer = loader.loadModel("models/pointer")
        self.pointer.reparentTo(render)
        self.pointer.setLightOff()
        self.pointer.setScale(0.3)
        #self.pointer.setScale(0.4)
    
        #level
        self.map=loader.loadModel("models/"+myFile)
        self.map.reparentTo(render)
        
        #camera
        base.disableMouse()  
        self.cameraNode  = NodePath(PandaNode("cameraNode"))
        self.cameraNode.reparentTo(render)
        self.cameraNode.setPos(0, 0, 32)
        base.camera.setPos(0,-32, 32)
        base.camera.lookAt(0, 0, 0)
        base.camera.wrtReparentTo(self.cameraNode)        
        
        self.keyMap = { "w" : False,
                        "s" : False,
                        "a" : False,
                        "d" : False, 
                        "q" : False,
                        "e" : False,
                        "z" : False,
                        "x" : False
                        }
        for key in self.keyMap.keys():
            self.accept(key, self.keyMap.__setitem__, [key, True])
            self.accept(key+"-up", self.keyMap.__setitem__, [key, False]) 
        self.camera_momentum=[1.0, 1.0, 1.0, 1.0]
        
        #the plane will bu used to see where the mouse pointer is
        self.plane = Plane(Vec3(0, 0, -0.1), Point3(0, 0, -0.1))   
        
        self.accept("mouse1", self.add_wall)
        self.accept("escape", self.remove_wall)
        self.accept("tab", self.waypoint_switch)
        self.accept("space", self.edit_mode_switch)
        self.accept("enter", self.generate_map, [myFile])   
        
        self.walls=[]
        self.wall=loader.loadModel("models/wall_w_collision2")       
        self.wall.setScale(0.3)
        self.wall.flattenLight()
        self.new_wall=True
        self.edit_mode="walls"
        
        self.spawnpoints=[]
        
        self.traverser = CollisionTraverser('myTraverser')
        #self.traverser.showCollisions(render)
        self.queue = CollisionHandlerQueue()  
        
        self.waypoints_connections=[] 
        self.waypoints=[]
        self.waypoint= NodePath(PandaNode("WPnode"))
        self.waypoint_model=loader.loadModel("models/waypoint")
        self.waypoint_model.setScale(0.3)
        self.waypoint_model.flattenLight()
        coll=self.waypoint_model.attachNewNode(CollisionNode('collRayNode'))        
        coll.node().addSolid(CollisionRay(0, 0, 25, 0,0,-180))
        coll.node().setIntoCollideMask(BitMask32.allOff()) 
        #coll.show()
        #self.traverser.addCollider(coll, self.queue)
        self.waypoint_model.reparentTo(self.waypoint)
        self.waypoint_model.setPos(-1, -1,0)
        self.outside=True
        
        #gui
        self.widget = DirectFrame(frameSize=(-32, 0, 0, 32),
                                    frameTexture='outside.png',
                                    state=DGG.NORMAL,
                                    parent=pixel2d)
        self.widget.setPos(32,0,-32)                     
        self.widget.setTransparency(TransparencyAttrib.MAlpha)        
        self.widget.bind(DGG.B1PRESS, self.waypoint_switch) 
        
        self.widget2 = DirectFrame(frameSize=(-32, 0, 0, 32),
                                    text="0.0 / 0.0",
                                    text_scale=20,                                  
                                    text_fg=(1,1,1,1),
                                    textMayChange=1,
                                    frameColor=(0, 0, 0, 0),
                                    parent=pixel2d)
        self.widget2.setPos(100,0,-22)                     
        self.widget2.setTransparency(TransparencyAttrib.MAlpha)
        
        self.polygons=[]
        self.current_polygon=[]
        self.undo=True
        self.timer=0
        
        taskMgr.add(self.__getMousePos, "mousePosTask")
        taskMgr.add(self.camera_control, "cameraTask")
        taskMgr.add(self.orient_wall, "orient_wall")   
    
    def edit_mode_switch(self):
        if self.edit_mode=="walls":
            self.edit_mode="spawnpoints"
        else:
            self.edit_mode="walls"
        print "Editing ", self.edit_mode 
    
    def build_polyset(self, points, position, tag=None, mask=1, z=0):
        polyset=render.attachNewNode(CollisionNode('collisionPolyset'))                         
        start_point=Point3(position[0], position[1], z)
        final_points=[]    
        for point in points:            
            final_points.append(Point3(point[0], point[1], z))
            #print point
        max=len(final_points)-1        
        for index in range(max): 
            polyset.node().addSolid(CollisionPolygon(start_point, final_points[index],final_points[index+1]))
        polyset.node().addSolid(CollisionPolygon(start_point, final_points[-1],final_points[0]))
        if tag!=None:    #tag could be 0, and we want a tag then
            polyset.setTag("index", str(tag))             
        polyset.node().setIntoCollideMask(BitMask32.bit(mask))  
        return polyset
    
    def run_collisions(self):
        #print "collisions..."
        self.traverser.traverse(render)                      
        for entry in self.queue.getEntries():            
            i_from=entry.getFromNodePath().getNetTag("index")
            i_into=entry.getIntoNodePath().getNetTag("index")
            if i_into!=i_from:                        
                self.waypoints_connections[int(i_from)].add(i_into)
                #print "connection: ", i_from, i_into
    
    def generate_map(self, name="temp"):
        VP=VisibilityPolygon()
        segments = VP.convertToSegments(self.polygons)        
        print "segments: ", segments
        export_node=NodePath(PandaNode("map"))        
        waypoints=[]
        for wp in render.findAllMatches("**/collRayNode*"):
            position = [wp.getX(render), wp.getY(render)]
            print "pos:",position 
            visibility = VP.compute(position, segments) 
            #print "visibility: ", visibility
            tag=wp.getNetTag("index")
            collision_poly=self.build_polyset(visibility, position, tag)
            collision_poly.reparentTo(export_node)  
            self.traverser.addCollider(wp, self.queue)             
            waypoints.append(export_node.attachNewNode(PandaNode("WP"+tag)))
            waypoints[-1].setPos(wp.getPos(render))
            #collision_poly.show()
        #export_node.writeBamFile('map2.bam') 
        export_node.reparentTo(render)        
        self.run_collisions()
        #we can build the graph data only after collisons 
        graph_data={}
        for i in range(len(waypoints)):            
            graph_data[str(i)]={}
            for item in self.waypoints_connections[i]:
                distance=waypoints[i].getDistance(waypoints[int(item)])
                #print distance
                graph_data[str(i)][item]=round(distance, 2)
        graph = Graph(graph_data)        
        #we can build the paths only when we have the graph data
        #so we run the loop AGAIN :| 
        for wp_index in range(len(waypoints)): 
            path_list=[]
            for i in range(len(waypoints)):
                path_list.append(round(graph.path_length(str(wp_index), str(i)), 2))            
            waypoints[wp_index].setTag("path", json.dumps(path_list))
            #print "path_list", wp_index, path_list
        #print graph_data
        
        #adding wals
        temp_wall=NodePath(PandaNode("walls")) 
        for wall in render.findAllMatches("**/collision"):
            wall.wrtReparentTo(temp_wall)
            wall.node().setIntoCollideMask(BitMask32.bit(2))  
        temp_wall.flattenStrong()
        temp_wall.wrtReparentTo(export_node)
        self.map.wrtReparentTo(export_node)
        
        #spawnpoints
        spawn=export_node.attachNewNode(PandaNode("spawnpoint_root"))
        for spawnpoint in self.spawnpoints:
            temp=spawn.attachNewNode(PandaNode("spawnpoint"))
            temp.setPos(spawnpoint.getPos(render))            
        #write
        export_node.writeBamFile('models/'+name+'.bam')         
        print "DONE"
        
    def close_polygon(self, point):
        x=point.getX()
        y=point.getY()
        if [x,y] in self.current_polygon:
            self.polygons.append(self.current_polygon)
            self.current_polygon=[]
            self.undo=False
            print  "new polygon added" 
            print self.polygons
        else:
            self.add_wall()
        
    def add_point(self, point):
        x=point.getX()
        y=point.getY()
        self.current_polygon.append([x,y])
        self.undo=True        
        #print  self.polygons
        #print  self.current_polygon
    
            
    def waypoint_switch(self, event=None):
        if self.outside:        
            self.waypoint_model.setPos(-1,1,0)
            self.outside=False
            self.widget['frameTexture']='inside.png'
        else:
            self.waypoint_model.setPos(-1,-1,0)
            self.outside=True
            self.widget['frameTexture']='outside.png'
                   
        
    def remove_wall(self):
        if self.edit_mode=="walls":
            if self.walls and self.undo:
                self.walls.pop().removeNode()
                self.waypoints.pop().removeNode()
                self.current_polygon.pop()
                self.new_wall=True
        else:
            if self.spawnpoints:
                self.spawnpoints.pop().removeNode()
            
    def add_wall(self):
        if self.edit_mode=="walls":
            if self.new_wall:
                self.walls.append(self.wall.copyTo(render))
                self.walls[-1].setPos(render, self.pointer.getPos())
                self.new_wall=False
                self.waypoints.append(self.waypoint.copyTo(render))
                self.waypoints[-1].setTag("index",str(len(self.waypoints)-1))
                self.waypoints[-1].setPos(render, self.pointer.getPos())
                self.add_point(self.pointer.getPos())
                self.waypoints_connections.append(set())
                #self.waypoints[-1].setPos(self.waypoints[-1],-1,1,0)            
            else:                        
                self.new_wall=True
                self.walls[-1].flattenLight()
                #self.add_point(self.pointer.getPos())
                self.close_polygon(self.pointer.getPos())
        else:
            self.spawnpoints.append(self.pointer.copyTo(render))
            print self.spawnpoints
            
    def orient_wall(self, task):
        if not self.new_wall:
            self.walls[-1].lookAt(self.pointer)
            self.waypoints[-1].lookAt(self.pointer)
            length=self.walls[-1].getDistance(self.pointer)
            if length!=0:
                self.walls[-1].setScale(1, length, 1)
        return task.cont
        
    def camera_control(self, task):
        dt = globalClock.getDt()
        for i in (0,1,2,3):
            if self.camera_momentum[i]>10.0:
                self.camera_momentum[i]=10.0
        #move X
        if self.keyMap["d"]:
            self.cameraNode.setX(self.cameraNode, 25*dt* self.camera_momentum[0])
            self.camera_momentum[0]+=dt*3        
        elif self.keyMap["a"]:
            self.cameraNode.setX(self.cameraNode, -25*dt* self.camera_momentum[0])
            self.camera_momentum[0]+=dt*3
        else:
            self.camera_momentum[0]=0
        #move Y    
        if self.keyMap["w"]:
            self.cameraNode.setY(self.cameraNode, 25*dt* self.camera_momentum[1])
            self.camera_momentum[1]+=dt*3         
        elif self.keyMap["s"]:
            self.cameraNode.setY(self.cameraNode, -25*dt* self.camera_momentum[1])
            self.camera_momentum[1]+=dt*3
        else:
            self.camera_momentum[1]=0
        #zoom    
        if self.keyMap["x"]:
            base.camera.setY(base.camera, -60*dt* self.camera_momentum[2])
            self.camera_momentum[2]+=dt*3
        elif self.keyMap["z"]:
            base.camera.setY(base.camera, 60*dt* self.camera_momentum[2])
            self.camera_momentum[2]+=dt*3
        else:
            self.camera_momentum[2]=0
        #rotate    
        if self.keyMap["q"]:    
            self.cameraNode.setH(self.cameraNode, -60*dt* self.camera_momentum[3])
            self.camera_momentum[3]+=dt*3
        elif self.keyMap["e"]:        
            self.cameraNode.setH(self.cameraNode, 60*dt* self.camera_momentum[3])
            self.camera_momentum[3]+=dt*3
        else:
            self.camera_momentum[3]=0     
      
        return task.cont

        
    def __getMousePos(self, task):
        if base.mouseWatcherNode.hasMouse():
          mpos = base.mouseWatcherNode.getMouse()
          pos3d = Point3()
          nearPoint = Point3()
          farPoint = Point3()
          base.camLens.extrude(mpos, nearPoint, farPoint)
          if self.plane.intersectsLine(pos3d,
            render.getRelativePoint(camera, nearPoint),
            render.getRelativePoint(camera, farPoint)):            
            self.pointer.setPos(render, (math.ceil(pos3d.getX()*2)/2, math.ceil(pos3d.getY()*2)/2, 0))            
            self.timer+=1
            if self.timer >=80:
                self.widget2['text']="x={0} y={1}".format(round(self.pointer.getX(),1), round(self.pointer.getY(),1) )
                self.timer=0
                
        return task.again   
        
w = AI_level_editor()
run() 
