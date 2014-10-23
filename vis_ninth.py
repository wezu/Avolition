import math

class VisibilityPolygon():
    def compute(self, position, segments):
        #print "compute"
        polygon = []
        sorted = self.sortPoints(position, segments);
        map=[-1] * len(segments)
        heap = []
        start = [position[0] + 1, position[1]]
        for i in xrange(len(segments)):
            a1 = self.angle(segments[i][0], position)
            a2 = self.angle(segments[i][1], position)
            active = False
            if (a1 > -180 and a1 <= 0 and a2 <= 180 and a2 >= 0 and a2 - a1 > 180):
                active = True
            if (a2 > -180 and a2 <= 0 and a1 <= 180 and a1 >= 0 and a1 - a2 > 180):
                active = True
            if active:
                self.insert(i, heap, position, segments, start, map)    
                #print i, " active"    
        i=0     
        #print "len(sorted): ",len(sorted)
        while i < (len(sorted)):
            #print i
            extend = False
            shorten = False
            orig = i
            vertex = segments[sorted[i][0]][sorted[i][1]]
            old_segment = heap[0]
            while (sorted[i][2] < sorted[orig][2] + self.epsilon()):
                if (map[sorted[i][0]] != -1):
                    if (sorted[i][0] == old_segment):
                        extend = True;
                        vertex = segments[sorted[i][0]][sorted[i][1]]                               
                    self.remove(map[sorted[i][0]], heap, position, segments, vertex, map);
                else:
                    self.insert(sorted[i][0], heap, position, segments, vertex, map)
                    if (heap[0] != old_segment):
                        shorten = True
                i+=1
                #print i
                if (i == len(sorted)):
                    break
            if extend:
                #print "extend"
                polygon.append(vertex)
                cur = self.intersectLines(segments[heap[0]][0], segments[heap[0]][1], position, vertex)
                if not self.equal(cur, vertex):
                    polygon.append(cur)
                    #print "extend"
            elif shorten:
                #print "shorten"
                polygon.append(self.intersectLines(segments[old_segment][0], segments[old_segment][1], position, vertex));
                polygon.append(self.intersectLines(segments[heap[0]][0], segments[heap[0]][1], position, vertex));         
                #print "shorten"
        return polygon
       
    def sortPoints(self, position, segments): 
        #print "sortPoints"    
        points=[-1] * (len(segments)*2)
        for i in xrange(len(segments)):
            for j in range(2):
                a=self.angle(segments[i][j], position)
                points[2*i+j] = [i, j, a]
        points.sort(key=lambda x: x[2]) # is this the same?? points.sort(function(a,b) {return a[2]-b[2];});
        return points
       
    def angle (self, a, b):
        #print "angle"
        return math.atan2(b[1]-a[1], b[0]-a[0]) * 180 / math.pi           
   
    def insert (self, index, heap, position, segments, destination, map):
        print "insert"
        intersect = self.intersectLines(segments[index][0], segments[index][1], position, destination)
        if len(intersect) == 0:
            return
        cur = len(heap)
        heap.append(index)
        map[index] = cur
        while (cur > 0):
            parent = self.parent(cur)
            if not self.lessThan(heap[cur], heap[parent], position, segments, destination):
                break               
            map[heap[parent]] = cur
            map[heap[cur]] = parent
            temp = heap[cur]
            heap[cur] = heap[parent]
            heap[parent] = temp
            cur = parent
           
       
    def intersectLines(self, a1, a2, b1, b2):
        #print "intersectLines:", a1, a2, b1, b2
        a1 = map(float, a1)
        a2 = map(float, a2)
        b1 = map(float, b1)
        b2 = map(float, b2)
        ua_t = (b2[0] - b1[0]) * (a1[1] - b1[1]) - (b2[1] - b1[1]) * (a1[0] - b1[0])
        ub_t = (a2[0] - a1[0]) * (a1[1] - b1[1]) - (a2[1] - a1[1]) * (a1[0] - b1[0])
        u_b  = (b2[1] - b1[1]) * (a2[0] - a1[0]) - (b2[0] - b1[0]) * (a2[1] - a1[1])
        if (u_b != 0):
            ua = ua_t / u_b
            ub = ub_t / u_b
            return [a1[0] - ua * (a1[0] - a2[0]), a1[1] - ua * (a1[1] - a2[1])]     
        return []
       
    def parent (self, index):
        #print "parent"
        return int(math.floor((index-1)/2))   
   
    def lessThan (self, index1, index2, position, segments, destination):
        #print "lessThan"
        inter1 = self.intersectLines(segments[index1][0], segments[index1][1], position, destination)
        inter2 = self.intersectLines(segments[index2][0], segments[index2][1], position, destination)
        if not self.equal(inter1, inter2):
            d1 = self.distance(inter1, position)
            d2 = self.distance(inter2, position)
            return d1 < d2
       
        end1 = 0
        if (self.equal(inter1, segments[index1][0])):
            end1 = 1
        end2 = 0
        if (self.equal(inter2, segments[index2][0])):
            end2 = 1
        a1 = self.angle2(segments[index1][end1], inter1, position)
        a2 = self.angle2(segments[index2][end2], inter2, position)
        if (a1 < 180):
            if (a2 > 180):
                return True
            return a2 < a1       
        return a1 < a2
       
    def equal (self, a, b):
        #print "equal"
        if (abs(a[0] - b[0]) < self.epsilon() and abs(a[1] - b[1]) < self.epsilon()):
            return True
        return False
       
    def epsilon (self):
        return 0.0000001  #is this crazy, or what?
       
    def distance (self, a, b):
        return (a[0]-b[0])*(a[0]-b[0]) + (a[1]-b[1])*(a[1]-b[1])
       
    def angle2(self, a, b, c):
        a1 = self.angle(a,b)
        a2 = self.angle(b,c)
        a3 = a1 - a2;
        if (a3 < 0):
            a3 += 360
        if (a3 > 360):
            a3 -= 360
        return a3
   
    def remove (self, index, heap, position, segments, destination, map):
        print "remove"
        map[heap[index]] = -1
        if (index == len(heap) - 1):
            heap.pop()
            return           
        heap[index] = heap.pop()
        map[heap[index]] = index
        cur = index
        parent = self.parent(cur)
        if (cur != 0 and self.lessThan(heap[cur], heap[parent], position, segments, destination)):
            TMI=1000
            while (cur > 0):                
                parent = self.parent(cur)
                #print parent, cur
                if not self.lessThan(heap[cur], heap[parent], position, segments, destination):
                    break                
                map[heap[parent]] = cur
                map[heap[cur]] = parent
                temp = heap[cur]
                heap[cur] = heap[parent]
                heap[parent] = temp
                cur = parent               
        else:
            while True:
                left = self.child(cur);
                right = left + 1;
                if (left < len(heap) and self.lessThan(heap[left], heap[cur], position, segments, destination) and
                   (right == len(heap) or self.lessThan(heap[left], heap[right], position, segments, destination))):
                   map[heap[left]] = cur
                   map[heap[cur]] = left
                   temp = heap[left]
                   heap[left] = heap[cur]
                   heap[cur] = temp
                   cur = left
                elif (right < len(heap) and self.lessThan(heap[right], heap[cur], position, segments, destination)):
                    map[heap[right]] = cur
                    map[heap[cur]] = right
                    temp = heap[right]
                    heap[right] = heap[cur]
                    heap[cur] = temp
                    cur = right
                else:
                    break
               
    def child (self,index):
        return 2*index+1   
   
    def convertToSegments (self, polygons):
        #print "convertToSegments"
        segments = []
        for i in xrange(len(polygons)):       
            for j in xrange(len(polygons[i])):
                k = j+1
                if (k == len(polygons[i])):
                    k = 0
                segments.append([polygons[i][j], polygons[i][k]])               
        return segments



if __name__ == '__main__':
    from PIL import Image, ImageDraw
    VP=VisibilityPolygon()
    polygons = []
   
   
    #polygons.append([[-1,-1],[501,-1],[501,501],[-1,501]])
    #polygons.append([[240,240],[260,240],[260,260],[240,260]])
    #polygons.append([[240,260],[260,260],[260,280],[240,280]])
    #polygons.append([[260,240],[280,240],[280,260],[260,260]])
    #polygons.append([[440,240],[460,240],[460,260],[440,260]])
    #polygons.append([[250,100],[260,140],[240,140]])
    #polygons.append([[280,100],[290,60],[270,60]])
    #polygons.append([[310,100],[320,140],[300,140]])
    #polygons.append([[50,450],[60,370],[70,450]])
    #polygons.append([[450,450],[460,370],[470,450]])
    #polygons.append([[50,50],[60,30],[70,50]])
    #polygons.append([[450,50],[460,30],[470,50]])
    #polygons.append([[140,340],[160,240],[180,340],[360,340],[360,360],[250,390],[140,360]])
    #polygons.append([[140,140],[150,130],[150,145],[165,150],[160,160],[140,160]])
    polygons.append([[-24.0, -5.0], [-25.5, -5.0], [-25.5, -4.0], [-24.0, -4.0]])
    polygons.append([[-24.0, 5.0], [-24.0, 4.0], [-25.5, 4.0], [-25.5, 5.0]])
    polygons.append([[-34.0, 4.0], [-43.0, 4.0], [-42.5, -4.0], [-34.0, -4.0], [-32.0, -12.0], [-29.0, -14.0], [-24.0, -14.0], [-24.0, -23.5], [-16.0, -23.5], [-16.0, -4.0], [4.0, -4.0], [4.0, 4.0], [-16.0, 4.0], [-16.0, 14.0], [-26.0, 14.0], [-26.0, 34.0], [-44.0, 34.0], [-44.0, 26.5], [-34.0, 26.0]])
    segments = VP.convertToSegments(polygons)
    position = [3, 3]
    visibility = VP.compute(position, segments)
    print visibility
    # Debug PIL Image out
    image = Image.new("RGBA", (500,500), (0,0,0,1))
    draw = ImageDraw.Draw(image)
    for i in xrange(1, len(polygons)):
        draw.polygon(map(tuple, polygons[i]), fill = 'red')
    draw.polygon(map(tuple, visibility), fill = 'white')
    draw.ellipse((position[0]-3, position[1]-3, position[0]+3, position[1]+3), fill='blue')
    del draw
    image.save("test.png", "PNG")