import xml.etree.ElementTree as ET  
from vector.vector import Vector
import math
class Geom:
    def __init__(self,geom):
        self.length = float(geom.attrib.get('length'))
        self.hdg = float(geom.attrib['hdg'])
        # tangent = Vector(math.sin(self.hdg), math.cos(self.hdg),0)
        # self.hdg = math.radians(tangent.argument())
        self.s = float(geom.attrib['s'])
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
        rep = rep + '   s: '+str(self.s)+'\n'
        rep = rep + '   length: '+str(self.length)+'\n'
        rep = rep + '   hdg: '+str(self.hdg)+'\n'
        rep = rep + '   origin: '+str(self.origin)+'\n'
        if self.type == 'line': rep = rep + '   line' +'\n'
        if self.type == 'arc' : rep = rep + '   arc: ' + str(self.curvature)+'\n'
        if self.type == 'spiral': rep = rep + '   spiral: '+str(self.init_curvature)+' '+str(self.final_curvature) +'\n'
        return rep
class RoadMark:
    def __init__(self, roadmark):
        self.sOffset = float(roadmark.attrib['sOffset'])
        self.type = roadmark.attrib['type']
        self.width = float(roadmark.attrib['width'])
        self.height = float(roadmark.attrib.get('height',0))
    def __repr__(self):
        rep = 'Road Mark: \n'
        rep = rep + '   type: '+str(self.type)+'\n'
        rep = rep + '   width: '+str(self.width)+'\n'
        rep = rep + '   height: '+str(self.height)+'\n'
        rep = rep + '   sOffset: '+str(self.sOffset)+'\n'
        return rep
class Lane:
    def __init__(self, lane):
        #self.scale = scale
        self.id = float(lane.attrib['id'])
        self.type = lane.attrib['type']
        self.level = lane.attrib['level'] if lane.attrib['level'] != 'false' else False
        self.a = 0
        self.b = 0
        self.c = 0
        self.d = 0
        self.sOffset = 0
        self.is_roadmark = False
        for width in lane.iter('width'):
            self.a = float(width.attrib['a'])
            self.b = float(width.attrib['b'])
            self.c = float(width.attrib['c'])
            self.d = float(width.attrib['d'])
            self.sOffset = float(width.attrib['sOffset'])
        for roadmark in lane.iter('roadMark'):
            self.road_mark = RoadMark(roadmark)
            self.is_roadmark = True

    def __repr__(self):
        str1='id: '+str(self.id)+' width: '+str(self.width) +'\n'
        str1 = str1 +'  '+str(self.road_mark)+'\n'
        return str1 
    def width(self,s):
        ds = s - self.sOffset if s>self.sOffset else 0
        return (self.a+self.b*ds+self.c*(ds**2)+self.d*(ds**3))

class LaneSection:
    def __init__(self, lane_section):
        self.s = float(lane_section.attrib['s'])
        self.lanes = self.get_lane_data(lane_section)
    
    def get_lane_data(self, lane_section):
        temp = []
        for lane in lane_section.iter('lane'):
            temp.append(Lane(lane))
        return temp
    def __repr__(self):
        str1=''
        str1 = str1+'Lane Section: '+'\n'
        str1 = str1 + ' s: '+str(self.s)+'\n'
        for lane in self.lanes:
            str1 = str1+' '+str(lane)+'\n'
        return str1
    def width(self,s):
        lanes = self.lanes
        lane_data = {'left':0,'right':0}
        lanes.sort(key=lambda x: x.id, reverse=False)
        temp = []
        for lane in lanes:
            if(lane.id > 0):
                temp.append(lane.width(s))  
        lane_data['right'] = temp
        lanes.sort(key=lambda x: x.id, reverse=True)
        temp = []
        for lane in lanes:
            if(lane.id < 0):
                temp.append(lane.width(s))  
        lane_data['left'] = temp
        return lane_data
    def get_valid_flag(self):
        lanes = self.lanes
        lanes.sort(key=lambda x: x.id, reverse=False)
        valid_flag_left = []
        valid_flag_right = []
        for lane in lanes:
            if(lane.id < 0):
                if(lane.type == 'border' or lane.a + lane.b + lane.c + lane.d == 0):
                    valid_flag_left.append(False)
                else:
                    valid_flag_left.append(True)
        lanes.sort(key=lambda x: x.id, reverse=True)
        for lane in lanes:
            if(lane.id > 0):
                if(lane.type == 'border' or lane.a + lane.b + lane.c + lane.d == 0):
                    valid_flag_right.append(False)
                else:
                    valid_flag_right.append(True)
        valid_flag_right.reverse()
        valid_flag = valid_flag_left + valid_flag_right

        return valid_flag
    

class Signal:
    def __init__(self, signal):
        self.s = float(signal.attrib['s'])
        self.t = float(signal.attrib['t'])
        self.name = signal.attrib.get('name', None)
        self.dynamic = signal.attrib.get('dynamic', None)
        self.orientation = signal.attrib.get('orientation',None) == '+' if signal.attrib.get('orientation',None) != None else None
        self.zOffset = float(signal.attrib.get('zOffset',0))
        self.country = signal.attrib.get('country', None)
        self.subtype = signal.attrib.get('subtype', None)
        self.value = float(signal.attrib.get('value',0))
        self.unit = signal.attrib.get('unit', None)
        self.hOffset = float(signal.attrib.get('hOffset',0))
        self.pitch = float(signal.attrib.get('pitch',0))
        self.roll = float(signal.attrib.get('roll',0))
        self.height = float(signal.attrib.get('height',0))
    def __repr__(self):
        str1=''
        str1 = str1+'Signal: '+'\n'
        str1 = str1 + ' s: '+str(self.s)+'\n'
        str1 = str1 + ' t: '+str(self.t)+'\n'
        str1 = str1 + ' name: '+str(self.name)+'\n'
        str1 = str1 + ' dynamic: '+str(self.dynamic)+'\n'
        str1 = str1 + ' orientation: '+str(self.orientation)+'\n'
        str1 = str1 + ' zOffset: '+str(self.zOffset)+'\n'
        str1 = str1 + ' type: '+str(self.type)+'\n'
        str1 = str1 + ' country: '+str(self.country)+'\n'
        str1 = str1 + ' subtype: '+str(self.subtype)+'\n'
        str1 = str1 + ' value: '+str(self.value)+'\n'
        str1 = str1 + ' unit: '+str(self.unit)+'\n'
        str1 = str1 + ' hOffset: '+str(self.hOffset)+'\n'
        str1 = str1 + ' pitch: '+str(self.pitch)+'\n'
        str1 = str1 + ' roll: '+str(self.roll)+'\n'
        str1 = str1 + ' height: '+str(self.height)+'\n'
        return str1

class Road:
    def __init__(self,road):
        self.name = road.attrib['name']
        self.length = float(road.attrib['length'])
        self.geom = self.__get_geometry_data__(road)
        self.lane_sections = self.__get_lane_sections_data__(road)
        self.signals = self.__get_signal_data__(road)
        self.elev = self.__get_elevation_data__(road)
    def __get_geometry_data__(self, road):
        temp = []
        for geometry in road.iter('geometry'):
            temp.append(Geom(geometry))
        return temp
    def __get_lane_sections_data__(self, road):
        temp = []
        for lane_section in road.iter('laneSection'):
            temp.append(LaneSection(lane_section))
        return temp
    def __get_signal_data__(self,road):
        temp=[]
        for signal in road.iter('signal'):
            temp.append(Signal(signal))
        return temp
    def __get_elevation_data__(self, road):
        elev_profile = road.find('elevationProfile')
        elev = elev_profile.find('elevation')
        res = {}
        if(elev != None):
            res['s'] = float(elev.attrib['s'])
            res['a'] = float(elev.attrib['a'])
            res['b'] = float(elev.attrib['b'])
            res['c'] = float(elev.attrib['c'])
            res['d'] = float(elev.attrib['d'])
        else:
            res ={'s':0,'a':0,'b':0,'c':0,'d':0}
        return(res)

    def get_geometry(self,s):
        s = s
        i = 0
        for geom in self.geom:
            if(i+1 == len(self.geom)):
                if(s > geom.s):
                    if(s <= geom.s + geom.length):
                        return geom
                    else:
                        return False
                else:
                    return False
            if s > geom.s and s < geom.s + geom.length:
                return geom
        return False
        
    def get_lane_data(self,s):
        s = s
        i = 0
        for lane_section in self.lane_sections:
            if(i+1 == len(self.lane_sections)):
                if(s < self.length):
                    res = lane_section.width(s)
                    return res
                else:
                    return False
            if s > lane_section.s and s < self.lane_sections[i+1].s:
                res = lane_section.width(s)
                return res
            i += 1
        return None
    
    def get_elevation(self,s):
        ds = s - self.elev['s'] if s > self.elev['s'] else 0
        return (self.elev['a'] + self.elev['b']*ds + self.elev['c']*(ds**2)+self.elev['d']*(ds**3))

    def get_pt_tangent(self,s,t):
        def TransformSTtoXY(s, t, roadType, start_s,args):
    # args = [origin, heading,length,CurvStart, CurvEnd]
            if roadType == 'line':
                tangent = Vector(math.cos(args[1]), math.sin(args[1]), 0)
                tangent = tangent.normalize()
                left_normal = tangent.rotate(90)
                pt = (s - start_s)*tangent + t*left_normal + args[0]

            elif roadType == 'arc':
                R = 1/args[3]
                anti_clockwise = 1
                if R<0 : anti_clockwise = -1
                if s < start_s: print('yes')
                theta = (s - start_s)/R
                tangent = Vector(math.cos(args[1]), math.sin(args[1]), 0)
                tangent = tangent.normalize()
                init_normal = tangent.rotate(anti_clockwise*90)
                centre = args[0] + init_normal*abs(R)
                pt_vec = args[0] - centre
                pt_vec = pt_vec.normalize()
                rot_pt_vec = pt_vec.rotate(180*theta/math.pi)
                tangent = tangent.rotate(180*theta/math.pi)
                pt = (abs(R)-t)*rot_pt_vec + centre

            elif roadType == 'spiral':
                if args[3] == 0:
                    ltoc = True
                    R = 1/args[4]
                else:
                    ltoc = False
                    R = 1/args[3]

                anti_clockwise = 1
                if R<0 : anti_clockwise = -1

                a = 1 / math.sqrt(2 * args[2] * abs(R))  # Scale factor

                RESOLUTION = 0.1
                num_sections = 1000
                distance = 0
                ahead = 1
                done = False
                scaling = 1
                length = args[2]
                dx = length/num_sections
                prev_point = args[0]
                for i in range(num_sections):
                    if ltoc:
                        pt_hdg = anti_clockwise*(distance*a)**2 + args[1]
                    else:
                        pt_hdg = anti_clockwise*((length*a)**2-((length-distance)*a)**2) + args[1]
                    tangent = Vector(math.cos(pt_hdg), math.sin(pt_hdg), 0)
                    t_norm = tangent.normalize()
                    pt = prev_point + ahead*dx*t_norm
                    prev_point = pt 
                    distance += ahead*dx*scaling
                    if distance > s - start_s:
                        break
                left_normal = t_norm.rotate(90)
                pt = left_normal*t + pt

            x = pt.x
            y = pt.y
            return pt,tangent
        geom = self.get_geometry(s)
        if(geom == False):
            return None,None
        elif(geom.type == 'line'):
            pt,tangent = TransformSTtoXY(s,t,'line',geom.s,[geom.origin,geom.hdg,geom.length])
        elif (geom.type == 'arc'):
            pt,tangent = TransformSTtoXY(s,t,'arc',geom.s,[geom.origin,geom.hdg,geom.length,geom.curvature])
        elif (geom.type == 'spiral'):
            pt,tangent = TransformSTtoXY(s,t,'spiral',geom.s,[geom.origin,geom.hdg,geom.length,geom.init_curvature,geom.final_curvature]) #Need not scale s,t, because it uses length not s,t and length is scaled, only works for scaling > 1, shitty fix IK
        return pt,tangent
    
    # def get_pt_tangent_lane(self,s,t):
    #     def TransformSTtoXY(s, t, roadType, start_s,length,curvInit = 0, curvEnd = 0):
    # # args = [origin, heading, length, CurvStart, CurvEnd]
    #         if(s > start_s + length):
    #             return None, None
    #         if roadType == 'line':
    #             tangent = Vector(1,0,0)
    #             tangent = tangent.normalize()
    #             left_normal = tangent.rotate(90)
    #             pt = (s - start_s)*tangent + t*left_normal

    #         elif roadType == 'arc':
    #             R = 1/curvInit
    #             anti_clockwise = 1
    #             if R<0 : anti_clockwise = -1
    #             theta = (s - start_s)/R
    #             tangent = Vector(1,0,0)
    #             tangent = tangent.normalize()
    #             init_normal = tangent.rotate(anti_clockwise*90)
    #             centre = init_normal*abs(R)
    #             pt_vec = - centre
    #             pt_vec = pt_vec.normalize()
    #             rot_pt_vec = pt_vec.rotate(180*theta/math.pi)
    #             tangent = tangent.rotate(180*theta/math.pi)
    #             pt = (abs(R)-t)*rot_pt_vec

    #         elif roadType == 'spiral':
    #             if curvStart == 0:
    #                 ltoc = True
    #                 R = 1/curvEnd
    #             else:
    #                 ltoc = False
    #                 R = 1/curvStart

    #             anti_clockwise = 1
    #             if R<0 : anti_clockwise = -1

    #             a = 1 / math.sqrt(2 * length * abs(R))  # Scale factor

    #             RESOLUTION = 0.1
    #             num_sections = 1000
    #             distance = 0
    #             ahead = 1
    #             done = False
    #             scaling = 1
    #             dx = length/num_sections
    #             prev_point = Vector(0,0,0)
    #             for i in range(num_sections):
    #                 if ltoc:
    #                     pt_hdg = anti_clockwise*(distance*a)**2 
    #                 else:
    #                     pt_hdg = anti_clockwise*((length*a)**2-((length-distance)*a)**2)
    #                 tangent = Vector(math.cos(pt_hdg), math.sin(pt_hdg), 0)
    #                 t_norm = tangent.normalize()
    #                 pt = prev_point + ahead*dx*t_norm
    #                 prev_point = pt 
    #                 distance += ahead*dx*scaling
    #                 if distance > s - start_s:
    #                     break
    #             left_normal = t_norm.rotate(90)
    #             pt = left_normal*t + pt

    #         x = pt.x
    #         y = pt.y
    #         return pt,tangent
    #     geom = self.get_geometry(s)
    #     if(geom.type == 'line'):
    #         pt,tangent = TransformSTtoXY(s,t,'line',geom.s,geom.length,[geom.origin,geom.hdg])
    #     elif (geom.type == 'arc'):
    #         pt,tangent = TransformSTtoXY(s,t,'arc',geom.s,geom.length[geom.origin,geom.hdg,geom.curvature])
    #     elif (geom.type == 'spiral'):
    #         pt,tangent = TransformSTtoXY(s,t,'spiral',geom.s,geom.length[geom.origin,geom.hdg,geom.init_curvature,geom.final_curvature]) #Need not scale s,t, because it uses length not s,t and length is scaled, only works for scaling > 1, shitty fix IK
    #     return pt,tangent
       


if(__name__ == "__main__"):
    tree = ET.parse('road_specification_v3.xodr')
    root = tree.getroot()
    i=0
    s= 3.666
    t =0
    for road in root.findall('road'):
        current_road = Road(road)
        print(current_road.lane_sections[0].get_valid_flag())
        

