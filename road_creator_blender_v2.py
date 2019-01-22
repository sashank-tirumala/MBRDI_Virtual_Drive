from vector.vector import Vector 
#from vector import Vector
import math
import bpy

import numpy as np
from xml_parse.xml_parse_v2 import *
import xml.etree.ElementTree as ET  

#import matplotlib
#import matplotlib.pyplot as plt
# from scipy.special import fresnel
def create_straight_line(length,lane_data,quad_number = 10):
    """ Gives the chord line set of points for a straight road"""
    tangent = Vector(1,0,0)
    pt= Vector(0,0,0)
    tot_lane_vertices = []
    for i in range(quad_number+1):
        lane_verts = generate_lane_verts(pt, tangent, lane_data)
        tot_lane_vertices.append(lane_verts)
        pt = pt + tangent * (length/quad_number)
        
    return tot_lane_vertices
def create_arc(length, curvature,lane_data, quad_number = 10):
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
    for i in range(quad_number + 1):
        pt = center + radius
        lane_pts = generate_lane_verts(pt,radius.rotate(90*anti_clockwise),lane_data)
        tot_lane_vertices.append(lane_pts)
        radius = radius.rotate((end_angle-start_angle)/quad_number)
        plt[0].append(pt.x)
        plt[1].append(pt.y)
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
def create_spiral_road(length,curvStart, curvEnd, lane_data, quad_number =10):
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
            pt_hdg = -(length*a)**2-anti_clockwise*((length-distance)*a)**2 + hdg
        tangent = Vector(math.cos(pt_hdg), math.sin(pt_hdg), 0)
        t_norm = tangent.normalize()
        pt = prev_point + ahead*dx*t_norm
        prev_point = pt 
        distance += ahead*dx
        total_pts.append(generate_lane_verts(pt,tangent,lane_data))
    return total_pts
# def spiral_line_to_curve(length,curvEnd, lane_data, quad_number =10):
#     '''Gives the set of chord line set of points for a spiral road when curvature starts from 0 to target'''
#     tangent = Vector(1,0,0) #vec
#     anti_clockwise = 1
#     print(tangent.argument())
#     Ltot = length                  # Length of curve
#     Rend = 1 / curvEnd             # Radius of curvature at end of spiral
#     distance = 0
#     if (Rend < 0 ): anti_clockwise = -1
#     total_pts = []
#     data = [[],[]]
#     a = 1 / math.sqrt(2 * Ltot * abs(Rend))  # Scale factor
    
#     # print final heading #
#     Ltot = Ltot * a
#     x,y = fresnel(Ltot)
#     fin = Vector(x/a,y/a,0)
#     fin = fin.rotate(tangent.argument())
#     print(fin)
#     print(Ltot**2)
#     for i in range(quad_number + 1):
#         # Rescale, compute and unscale
#         distance_scaled = distance * a # Distance along normalised spiral
#         deltax_scaled, deltay_scaled = fresnel(distance_scaled)
#         pt = Vector(deltax_scaled/a, deltay_scaled/a*anti_clockwise,0)
#         distance += length/quad_number
#         current_tangent = Vector(math.cos(distance_scaled**2),math.sin(distance_scaled**2),0)
#         # deltax and deltay give coordinates for theta=0
#         pt = pt.rotate(tangent.argument())
#         current_tangent = current_tangent.rotate(tangent.argument())
#         # Spiral is relative to the starting coordinates
#         # total_pts.append(generate_lane_verts(pt, current_tangent, lane_data))
#         # data[0].append(pt.x)
#         # data[1].append(pt.y)

#         current_hdg = distance_scaled*distance_scaled*anti_clockwise
#         tangent = Vector(math.cos(current_hdg),math.sin(current_hdg),0)
#         total_pts.append(generate_lane_verts(pt,tangent,lane_data))
#         # distance = distance + length/quad_number
#     return total_pts
# def spiral_curve_to_line(length,curvStart, lane_data, quad_number =10):
#     '''Gives the set of chord line set of points for a spiral road when curvature starts from target to -ve'''
#     print('entered')
#     tangent = Vector(1,0,0) #vec
#     anti_clockwise = 1
#     print(tangent.argument())
#     Ltot = length                  # Length of curve
#     Rstart = 1 / curvStart             # Radius of curvature at end of spiral
#     distance = 0
#     if (Rstart < 0 ): anti_clockwise = -1
#     total_pts = []
#     a = 1 / math.sqrt(2 * Ltot * abs(Rstart))  # Scale factor
#     Ltot = Ltot * a
#     x,y = fresnel(Ltot)
#     if anti_clockwise == 1: 
#         final_hdg = -Ltot**2+3.14
#     if anti_clockwise == -1: 
#         final_hdg = Ltot**2-3.14
    
#     rot = - final_hdg +3.14
#     print('rot: ',rot)
#     tangent2 = Vector(math.cos(rot),math.sin(rot),0)
#     new_origin = -1* Vector(x/a,-1*anti_clockwise*y/a,0).rotate(Vector(math.cos(rot),math.sin(rot),0).argument())
#     print(new_origin)

#     for i in range(quad_number + 1):
#         # Rescale, compute and unscale
#         distance_scaled = distance * a # Distance along normalised spiral
#         deltax_scaled, deltay_scaled = fresnel(distance_scaled)
#         pt = Vector(deltax_scaled/a, deltay_scaled/a*-1*anti_clockwise,0)
#         distance += length/quad_number
#         # deltax and deltay give coordinates for theta=0
#         pt = pt.rotate(tangent2.argument())
#         # Spiral is relative to the starting coordinates
#         if anti_clockwise == 1: 
#             final_hdg = -distance_scaled**2+3.14
#         if anti_clockwise == -1: 
#             final_hdg = distance_scaled**2-3.14
    
#         rot = - final_hdg + 3.14
#         #current_hdg = hdg - distance_scaled*distance_scaled*anti_clockwise
#         tangent = Vector(math.cos(rot),math.sin(rot),0)
#         total_pts.append(generate_lane_verts(pt,tangent,lane_data))
#         # total_pts[0].append(pt.x)
#         # total_pts[1].append(pt.y)
#     return total_pts
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
def create_blender_mesh(verts, faces, origin,heading, road_number):
    name = "road_"+str(road_number)
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name,mesh)
    
    # #set mesh location
    obj.location = [origin.x,origin.y,origin.z]
    obj.rotation_euler = (0,0,heading)
    # object.location = [0,0,0]
    bpy.context.scene.objects.link(obj)
    
    # #create mesh from python data
    mesh.from_pydata(verts,[],faces)
    mesh.update(calc_edges=True)
if (__name__ == "__main__"):
    scale = 100
    xml_path = 'C:/Users/stsas/blensor_scripts/OpenDriveFiles/Crossing8Course.xodr'
    tree = ET.parse(xml_path)
    root = tree.getroot()
    i = 0
    for road in root.findall('road'):
        current_road = Road(road,scale)
        #lanes = []
        #for lane in road.iter('lane'):
            #lanes.append(Lane(lane, 100))
        #lane_data = get_lane_widths(lanes)
        i = 0 
        lane_data = current_road.lane_sections[0].width(0.01)
        for geom in current_road.geom:
            if geom.type == 'line':
                pts = create_straight_line(geom.length, lane_data)
            if geom.type == 'arc':
                pts = create_arc(geom.length,geom.curvature,lane_data)
            if geom.type == 'spiral':
                pts= create_spiral_road(geom.length, geom.init_curvature, geom.final_curvature, lane_data)
            verts = generate_blender_verts(pts)
            faces = generate_blender_faces(verts, lane_data)
            create_blender_mesh(verts,faces,geom.origin,geom.hdg,i)
            i+=1
    
    
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
