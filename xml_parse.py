import xml.etree.ElementTree as ET  
from vector.vector import Vector
import math
class Geom:
    def __init__(self,geom):
        self.length = float(geom.attrib['length'])
        self.hdg = float(geom.attrib['hdg'])
        # tangent = Vector(math.sin(self.hdg), math.cos(self.hdg),0)
        # self.hdg = math.radians(tangent.argument())
        self.origin = Vector(float(geom.attrib['x']), float(geom.attrib['y']), 0)
        for child in geom:
            self.type = child.tag
            if(self.type == 'arc'):
                self.curvature = float(child.attrib['curvature'])
            if(self.type == 'spiral'):
                self.init_curvature = float(child.attrib['curvStart'])
                self.final_curvature = float(child.attrib['curvEnd'])
    def __repr__(self):
        rep = 'Geometry: \n'
        rep = rep + '   length: '+str(self.length)+'\n'
        rep = rep + '   hdg: '+str(self.hdg)+'\n'
        rep = rep + '   origin: '+str(self.origin)+'\n'
        if self.type == 'line': rep = rep + '   line'
        if self.type == 'arc' : rep = rep + '    arc: ' + str(self.curvature)
        if self.type == 'spiral': rep = rep + '    spiral: '+str(self.init_curvature)+' '+str(self.final_curvature)
        return rep

class Lane:
    def __init__(self, lane):
        self.id = float(lane.attrib['id'])
        self.type = lane.attrib['type']
        self.level = float(lane.attrib['level'])
        self.width = 0
        for width in lane.iter('width'):
            self.width = float(width.attrib['a'])
    def __repr__(self):
        str1='id: '+str(self.id)+' width: '+str(self.width)
        return str1 

def get_lane_widths(lanes):
    lane_data = {'left':0,'right':0}
    lanes.sort(key=lambda x: x.id, reverse=False)
    temp = []
    for lane in lanes:
        if(lane.id > 0):
            temp.append(lane.width)  
    lane_data['right'] = temp
    lanes.sort(key=lambda x: x.id, reverse=True)
    temp = []
    for lane in lanes:
        if(lane.id < 0):
            temp.append(lane.width)  
    lane_data['left'] = temp
    return lane_data

# tree = ET.parse('test1.xodr')
# root = tree.getroot()
# geoms = []
# lanes = []
# for road in root.findall('road'):
#     for lane in road.iter('lane'):
#         lanes.append(Lane(lane))
# print(lanes)

# print(get_lane_widths(lanes))
        
