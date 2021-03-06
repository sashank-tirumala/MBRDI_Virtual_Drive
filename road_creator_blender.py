from vector.vector import Vector 
#from vector import Vector
import math
import bpy

import numpy as np
from xml_parse.xml_parse import *
from prop_handler.prop_handler import PropHandler
import xml.etree.ElementTree as ET  

#import matplotlib
#import matplotlib.pyplot as plt
# from scipy.special import fresnel
def create_straight_line(length,current_road,start_s,hardCode = False,quad_number = 10):
    """ Gives the chord line set of points for a straight road"""
    tangent = Vector(1,0,0)
    pt= Vector(0,0,0)
    tot_lane_vertices = []
    s = -0.1
    for i in range(quad_number+1):
        lane_data = current_road.get_lane_data(s+start_s)
        # print(lane_data)
        current_pt = pt + Vector(0,0,current_road.get_elevation(s + start_s))
        lane_verts = generate_lane_verts(current_pt, tangent, lane_data,hardCode)
        tot_lane_vertices.append(lane_verts)
        pt = pt + tangent * (length/quad_number)
        s = s + length/quad_number       
    return tot_lane_vertices
def create_arc(length, curvature, current_road,start_s, hardCode = False, quad_number = 10):
    """ Gives the chord line set of points for a curved road"""
    plt = [[],[]]
    
    anti_clockwise = 1
    tangent = Vector(1,0,0)
    radius = 1 / curvature
    end_angle = 0
    if(radius > 0):
        tangent = tangent.rotate(90)
        anti_clockwise = 1
    else:
        tangent = tangent.rotate(-90)
        radius = -1 * radius
        anti_clockwise = -1
    center = radius*tangent
    tangent = tangent.rotate(180)
    start_angle = tangent.argument()
    end_angle = start_angle + anti_clockwise*360*(length/(2*math.pi*radius))
    angle = start_angle    
    radius = Vector(radius,0,0)
    radius = radius.rotate(start_angle)
    tot_lane_vertices = []
    s = -0.1
    for i in range(quad_number + 1):
        pt = center + radius
        lane_data = current_road.get_lane_data(s+start_s)
        current_pt = pt + Vector(0,0,current_road.get_elevation(s + start_s))
        lane_pts = generate_lane_verts(current_pt,radius.rotate(90*anti_clockwise),lane_data, hardCode)
        tot_lane_vertices.append(lane_pts)
        radius = radius.rotate((end_angle-start_angle)/quad_number)
        plt[0].append(pt.x)
        plt[1].append(pt.y)
        dTheta = (end_angle - start_angle)/quad_number
        dTheta = dTheta * 3.14 / 180
        s = s + radius.norm() * dTheta
    return tot_lane_vertices
def fresnel(L):
    h = 0.01
    s = lambda x: np.sin(x**2)
    c = lambda x: np.cos(x**2)
    sums = 0
    for i in np.arange(0,L,0.01):
        sums += s(i)
    sans = h*(0.5*s(0)+sums+0.5*s(L))
    sums = 0
    for i in np.arange(0,L,0.01):
        sums += c(i)
    cans = h*(0.5*c(0)+sums+0.5*c(L))
    return cans, sans
def create_spiral_road(length,curvStart, curvEnd,current_road,start_s, hardCode = False,quad_number =10):
    # if(curvStart==0):
    #     return spiral_line_to_curve(length,curvEnd,lane_data)
    # else:
    #     return spiral_curve_to_line(length,curvStart,lane_data)
    origin = Vector(0,0,0)
    hdg = 0
    if curvStart == 0:
        ltoc = True
        R = 1/curvEnd
    else:
        ltoc = False
        R = 1/curvStart
    anti_clockwise = 1
    if R<0 : anti_clockwise = -1
    a = 1 / math.sqrt(2 * length * abs(R))  # Scale factor
    RESOLUTION = 0.1
    num_sections = 100
    distance = 0
    ahead = 1
    done = False
    scaling = 1
    dx = length/num_sections
    prev_point = origin
    total_pts = []
    for i in range(num_sections):
        if ltoc:
            pt_hdg = anti_clockwise*(distance*a)**2 + hdg
        else:
            pt_hdg = anti_clockwise*((length*a)**2-((length-distance)*a)**2) + hdg
        tangent = Vector(math.cos(pt_hdg), math.sin(pt_hdg), 0)
        t_norm = tangent.normalize()
        pt = prev_point + ahead*dx*t_norm
        prev_point = pt 
        distance += ahead*dx
        lane_data = current_road.get_lane_data(distance + start_s)
        current_pt = pt + Vector(0,0,current_road.get_elevation(distance + start_s))
        total_pts.append(generate_lane_verts(current_pt,tangent,lane_data,hardCode))
    return total_pts
def generate_blender_verts(verts,scale):
    res_verts = []
    for lane_verts in verts:
        for vertex in lane_verts:
            res_verts.append((vertex.x/scale,vertex.y/scale,vertex.z/scale))
    return res_verts

def generate_blender_faces(blender_verts, valid_flag, lane_data):
    no_of_lanes = len(lane_data['left'])+len(lane_data['right'])
    #no_of_lanes = 4
    i = 0
    faces = []
    count = 0
    #print(valid_flag)
    while(i<len(blender_verts)-no_of_lanes-1):
        if(count < no_of_lanes):
            if(valid_flag[count] == True):
                A = i
                B = i + 1
                C = i + (no_of_lanes+1) + 1
                D = i + (no_of_lanes+1)

                face = [A,B,C,D]
                faces.append(face)
                count = count + 1
            else:
                count = count + 1
        else:
            count = 0
        i +=1
        
    return faces
def generate_lane_verts(pt, tangent, lane_data, hard_code):
    result_pts= []
    result_pts.append(pt)
    tangent = tangent.normalize()
    left_normal = tangent.rotate(90)
    right_normal = tangent.rotate(-90)
    new_pt = pt
    #print(lane_data)
    for x in lane_data['left']:
        new_pt = new_pt + left_normal*x
        result_pts.append(new_pt)
    result_pts = list(reversed(result_pts))
    new_pt=pt
    for x in lane_data['right']:
        new_pt = new_pt + right_normal*x
        result_pts.append(new_pt)
    if(hard_code):
        if len(result_pts) == 11:
            del result_pts[0]
            #print('ENTER')
        #if len(result_pts) == 11:
            #del result_pts[10]
            #del result_pts[9]
            
    return result_pts

def create_blender_mesh(verts, faces, origin,heading, road_number, color):
    name = "road_"+str(road_number)
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name,mesh)
    
    # #set mesh location
    obj.location = [origin.x,origin.y,origin.z]
    obj.rotation_euler = (0,0,heading)
    # object.location = [0,0,0]
    bpy.context.scene.objects.link(obj)
    mat = bpy.data.materials.new(name="Material")
    obj.data.materials.append(mat)
    obj.data.materials[0].diffuse_color = color
    # #create mesh from python data
    mesh.from_pydata(verts,[],faces)
    mesh.update(calc_edges=True)
def generate_lane_mark_verts(pt, tangent, lane_data, width, lane_marking = False):
    result_pts= []
    tangent = tangent.normalize()
    left_normal = tangent.rotate(90)
    right_normal = tangent.rotate(-90)
    #print(lane_data)
    pt = pt + Vector(0,0,0.01)
    result_pts.append(pt + (-1*width)*left_normal)
    result_pts.append(pt + (width)*left_normal)
    
    new_pt = pt
    for x in lane_data['left']:
        new_pt = new_pt + x*left_normal
        new_pt1 = new_pt + (-1*width)*left_normal
        new_pt2 = new_pt + (width)*left_normal
        result_pts.append(new_pt1)
        result_pts.append(new_pt2)
    result_pts = list(reversed(result_pts))
    new_pt=pt
    for x in lane_data['right']:
        new_pt = new_pt + x*right_normal
        new_pt1 = new_pt + (-width)*right_normal
        new_pt2 = new_pt + (+width)*right_normal
        
        result_pts.append(new_pt1)
        result_pts.append(new_pt2)
    return result_pts

def get_lane_valid_flag(lanes ,strip_length, mark_length):
    lanes.sort(key=lambda x: x.id, reverse=False)
    vf = []
    valid_flag = []
    for lane in lanes:
        if(not lane.is_roadmark):
            valid_flag.append(False)
        elif lane.road_mark.type == 'solid':
            valid_flag.append(True)
        elif lane.road_mark.type == 'broken' and strip_length >=0:
            valid_flag.append(True)
        elif lane.road_mark.type == 'broken' and strip_length < 0:
            valid_flag.append(False)
        elif lane.road_mark.type == 'none':
            valid_flag.append(False)
    return valid_flag
def generate_lane_faces(blender_verts,valid_flag, lane_data):
    no_of_lanes = len(lane_data['left'])+len(lane_data['right'])+1
    i = 0
    faces = []
    count = 0
    count_sections = 0
    while(count_sections < len(valid_flag) and i +len(valid_flag[count_sections])*2 + 1< len(blender_verts)):
        if(count < len(valid_flag[count_sections])):
           
            if(valid_flag[count_sections][count] == True):
                A = i
                B = i + 1
                C = i + (len(valid_flag[count_sections]))*2 + 1
                D = i + (len(valid_flag[count_sections]))*2 

                face = [A,B,C,D]
                faces.append(face)
                count = count + 1
            else :
               
                count += 1
            i += 2
        else:
            
            count = 0
            count_sections += 1
        
        
    return faces

if (__name__ == "__main__"):
    bpy.data.scenes['Scene'].render.engine = 'CYCLES'
    grey = ((0,0,0))
    white = ((1,1,1))
    scale = 10
    obj_scale = 10
    xml_path = 'C:/Users/stsas/blensor_scripts/OpenDriveFiles/Crossing8Course.xodr'
    tree = ET.parse(xml_path)
    root = tree.getroot()
    i = 0
    mark_length = 10
    hard_code = False
    valid_flag = 0
    signal_counter = 0
    for road in root.findall('road'):
        current_road = Road(road)
        #lanes = []
        #for lane in road.iter('lane'):
            #lanes.append(Lane(lane, 100))
        #lane_data = get_lane_widths(lanes)
        i = 0 
        lane_data = current_road.lane_sections[0].width(0.01)
        valid_flag = current_road.lane_sections[0].get_valid_flag()
        for geom in current_road.geom:
            if geom.type == 'line':
                pts = create_straight_line(geom.length, current_road,geom.s)
            if geom.type == 'arc':
                pts= create_arc(geom.length,geom.curvature,current_road,geom.s)
            if geom.type == 'spiral':
                pts= create_spiral_road(geom.length, geom.init_curvature,geom.final_curvature, current_road,geom.s)
            verts = generate_blender_verts(pts, scale)
            faces = generate_blender_faces(verts,valid_flag, lane_data)
            create_blender_mesh(verts,faces,geom.origin/scale,geom.hdg,i,grey)
            i+=1
        ph = PropHandler()
        for signal in current_road.signals:
            orig,tangent = current_road.get_pt_tangent(signal.s,signal.t)
            #road_origin = current_road.geom[0].origin
            print(orig)
            #ph.place((orig)/scale, math.radians(tangent.rotate(-90).argument()), obj_scale, signal.name, signal_counter)
            signal_counter += 1

    
    strip_length = mark_length
    for road in root.findall('road'):
        allverts= [ ]
        valid_flag = []
        currentRoad = Road(road)
        for s in np.arange(0, currentRoad.length, currentRoad.length/100):
            lane_data = currentRoad.get_lane_data(s)
            currentRoad.lane_sections[0].lanes
            pt,tangent = currentRoad.get_pt_tangent(s,0)
            elev = currentRoad.get_elevation(s)
            lane_data = currentRoad.get_lane_data(s)
            if(pt != None):
                new_pt = pt + Vector(0,0,elev)
                allverts.append(generate_lane_mark_verts(new_pt,tangent,lane_data, 0.5))
                valid_flag.append(get_lane_valid_flag(currentRoad.lane_sections[0].lanes, strip_length, mark_length))
                #print(len(allverts))
            #print(pt)
            #allverts.append(pt)
            strip_length -= currentRoad.length/100
            if(strip_length < -mark_length):
                strip_length = mark_length
        verts = generate_blender_verts(allverts,scale)
        faces = generate_lane_faces(verts, valid_flag, lane_data)
        create_blender_mesh(verts,faces,Vector(0,0,0),0,0,white)


    # origin = Vector(0,0,0)
    # heading =0
    # valid_flag = [True, False, True, False]
    # verts = [(0,0,0),(1,0,0),(2,0,0),(3,0,0),(4,0,0),
    #         (0,1,0),(1,1,0),(2,1,0),(3,1,0),(4,1,0),
    #         (0,2,0),(1,2,0),(2,2,0),(3,2,0),(4,2,0)]
    # faces = generate_blender_faces(verts,valid_flag)    
    # create_blender_mesh(verts, faces, origin,heading, '1')
    # allverts= [ ]
    # strip_length = mark_length
    # valid_flag = []
    # i = 0
    # for road in root.findall('road'):
    #     currentRoad = Road(road)
    #     lanes = currentRoad.lane_sections[0].lanes
    #     for geom in current_road.geom:
    #         if geom.type == 'line':
    #             pts, valid_flag = create_straight_line_lane(geom.length, current_road)
    #         if geom.type == 'arc':
    #             pts, valid_flag = create_arc_lane(geom.length,geom.curvature,current_road)
    #         if geom.type == 'spiral':
    #             pts, valid_flag= create_spiral_lane(geom.length, geom.init_curvature, geom.final_curvature, current_road)
    #         verts = generate_blender_verts(pts, scale)
    #         faces = generate_lane_faces(verts,valid_flag, lane_data)
    #         create_blender_mesh(verts,faces,geom.origin/scale,geom.hdg,i)
    #         i+=1

    




    
    
    #BLENDER TEST CODE
    # o = Vector(0,0,0)
    # heading = 0
    # length = 2.5
    # arc_length = 1.57
    # curvature = 0
    # curvStart = -2
    # curvEnd = 0
    # lane_data = {}
    # lane_data['left'] = [0.1,0.1,0.1]
    # lane_data['right'] = [0.1]
    # pts = spiral_line_to_curve(o,heading,length,-2,lane_data)
    #pts = create_arc(o,heading,arc_length,curvature,lane_data)
    # verts = generate_blender_verts(pts)
    # faces = generate_blender_faces(verts, lane_data)
    # create_blender_mesh(verts, faces, o, 1)

    
    #MATPLOTLIB CODE
    # data = create_spiral_road(o,heading, length,curvStart, curvEnd, lane_data)
    # # data = create_arc(o,heading,length,curvStart, curvEnd, lane_data)
    # fig, ax = plt.subplots()
    # ax.plot(data[0], data[1])
    # ax.set(xlabel='x_coord', ylabel='y_coord',
    #     title='Chord_Line of Road')
    # ax.grid()
    # fig.savefig("test.png")
    # plt.show()
