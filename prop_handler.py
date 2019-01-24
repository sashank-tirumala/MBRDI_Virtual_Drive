from vector.vector import Vector
import bpy
class PropHandler():
    def __init__(self):
        self.paths= {'Sg274Hoechstgeschw30_03.flt' : './sketchup_models/120_sign.dae',
        'Sg451.flt' : './sketchup_models/200m_blue_sign.dae',
        'Sg332Ausfahrttafel.flt' : './sketchup_models/exit_sign.dae',
        'Sg331Kraftfahrstr03.flt' : './sketchup_models/double_speed_limit.dae',
        'Sg274Hoechstgeschw50_03.flt' : './sketchup_models/signal_final.dae',
        'Sg113Schneeglaette01.flt' : './sketchup_models/double_speed_limit.dae',
        'car':'./sketchup_models/car.dae'}
    def place(self,origin,angle,scale,id,id_no):
        bpy.ops.wm.collada_import(filepath=self.paths[id])
        bpy.context.selected_objects[0].name = id + str(id_no)
        bpy.data.objects[id + str(id_no)].location = [origin.x,origin.y,origin.z]
        #bpy.data.objects[id].rotation_euler[2] = angle
        bpy.data.objects[id + str(id_no)].scale = [s/scale for s in bpy.data.objects[id + str(id_no)].scale]
        
    

if(__name__ == "__main__"):
    ph = PropHandler()
    v = Vector(3,3,0)
    angle = 3.14
    ph.place(v,angle,1,'2')
