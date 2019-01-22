from vector.vector import Vector 
#from vector import Vector
import math
# import bpy

import numpy as np
from xml_parse.xml_parse_v3 import *
import xml.etree.ElementTree as ET  

#import matplotlib
#import matplotlib.pyplot as plt
# from scipy.special import fresnel


def TransformSTtoXY(s, t, roadType, args):
    # args = [origin, heading, length, CurvStart, CurvEnd]
    if roadType == 'line':
        tangent = Vector(math.cos(args[1]), math.sin(args[1]), 0)
        tangent = tangent.normalize()
        left_normal = tangent.rotate(90)
        pt = s*tangent + t*left_normal + args[0]
    elif roadType == 'arc':
        R = 1/args[3]
        hdg = args[1]
        origin = args[0]
        anti_clockwise = 1
        if R<0 : anti_clockwise = -1
        theta = s/R
        tangent = Vector(math.cos(hdg), math.sin(hdg), 0)
        tangent = tangent.normalize()
        init_normal = tangent.rotate(anti_clockwise*90)
        centre = origin + init_normal*R
        #center = init_normal*R
        pt_vec = origin - centre
        pt_vec = pt_vec.normalize()
        rot_pt_vec = pt_vec.rotate(180*theta/math.pi)
        pt = (R-t)*pt_vec + centre
    elif roadType == 'spiral':    
        Resolution = 0.1
        num_sections = 100
        distance = 0
        ahead = 1
        done = False
        scaling = 1
        dx = length/num_sections
        prev_point = args[0]
        for i in range(num_sections):
            if ltoc:
                pt_hdg = anti_clockwise*(distance*a)**2 + args[1]
            else:
                pt_hdg = -(length*a)**2-anti_clockwise*((length-distance)*a)**2 + args[1]
            tangent = Vector(math.cos(pt_hdg), math.sin(pt_hdg), 0)
            t_norm = tangent.normalize()
            pt = prev_point + ahead*dx*t_norm
            prev_point = pt 
            distance += ahead*dx*scaling
            if abs(distance-s) <= RESOLUTION:
                break
            elif distance > s:
                if ahead == 1:
                    scaling = scaling/2
                ahead = -1
            elif distance < s:
                if ahead == -1:
                    scaling = scaling/2
                ahead = 1
        left_normal = t_norm.rotate(90)
        pt = left_normal*t + pt

    x = pt.x
    y = pt.y
    return x,y
def generate_lane_verts(pt, tangent, lane_data):
    result_pts= []
    result_pts.append(pt)
    tangent = tangent.normalize()
    left_normal = tangent.rotate(90)
    right_normal = tangent.rotate(-90)
    new_pt = pt
    for x in lane_data['left']:
        new_pt = new_pt + left_normal*x
        result_pts.append(new_pt)
    result_pts = list(reversed(result_pts))
    new_pt=pt
    for x in lane_data['right']:
        new_pt = new_pt + right_normal*x
        result_pts.append(new_pt)
    return result_pts

def generate_blender_verts(verts):
    res_verts = []
    for lane_verts in verts:
        for vertex in lane_verts:
            res_verts.append((vertex.x,vertex.y,vertex.z))
    return res_verts

def generate_blender_faces(blender_verts, lane_data):
    no_of_lanes = len(lane_data['left'])+len(lane_data['right'])
    i = 0
    faces = []
    count = 0
    while(i<len(blender_verts)-no_of_lanes-1):
        if(count < no_of_lanes):
            A = i
            B = i + 1
            C = i + (no_of_lanes+1) + 1
            D = i + (no_of_lanes+1)

            face = [A,B,C,D]
            faces.append(face)
            count = count + 1
        else:
            count = 0
        i +=1
    return faces
def create_blender_mesh(verts, faces, origin,heading, road_number=0):
    name = "road_"+str(road_number)
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name,mesh)
    
    # #set mesh location
    obj.location = [origin.x,origin.y,origin.z]
    #obj.rotation_euler = (0,0,heading)
    #obj.location = [0,0,0]
    bpy.context.scene.objects.link(obj)
    
    # #create mesh from python data
    mesh.from_pydata(verts,[],faces)
    mesh.update(calc_edges=True)

if (__name__ == "__main__"):
    scale = 1
    xml_path = 'C:/Users/stsas/blensor_scripts/OpenDriveFiles/Crossing8Course.xodr'
    tree = ET.parse(xml_path)
    root = tree.getroot()
    # print('\n\n\n--Starting--')
    lane_data ={}
    for road in root.findall('road'):
        currentRoad = Road(road, 10)
        allverts = []
        for s in np.arange(0,currentRoad.length,currentRoad.length/100):
            pt,tangent = currentRoad.get_pt_tangent(s,0)
            lane_data = currentRoad.get_lane_data(s)
            allverts.append(generate_lane_verts(pt,tangent,lane_data))
        verts = generate_blender_verts(allverts)
        faces = generate_blender_faces(verts, lane_data)
        create_blender_mesh(verts,faces,Vector(0,0,0),0)


    # print(TransformSTtoXY(1, 5, 'arc', [Vector(0,0,0), math.pi/2, 10, Vector(0,0,0),0, 0.2]))
    
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
    # i = 0
    # x = []
    # y = []
    # while(i < 10):
    #     temp_x, temp_y = TransformSTtoXY(i,0,'arc',[Vector(0,0,0),1.57,5,0.1])
    #     print(temp_x, temp_y)
    #     i = i+ 0.1
    #     x.append(temp_x)
    #     y.append(temp_y)
    # # data = create_spiral_road(o,heading, length,curvStart, curvEnd, lane_data)
    # # data = create_arc(o,heading,length,curvStart, curvEnd, lane_data)
    # fig, ax = plt.subplots()
    # ax.plot(x,y)
    # ax.set(xlabel='x_coord', ylabel='y_coord',
    #     title='Chord_Line of Road')
    # ax.grid()
    # fig.savefig("test.png")
    # plt.show()