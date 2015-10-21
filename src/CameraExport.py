bl_info = {
    "name": "Camera animated parameters exporter for Urho3D",
    "author": "codingmonkey",
    "category": "Object",
    "blender": (2, 75, 4)   
}

import bpy
import os
import struct
import sys
import mathutils
from math import radians
from bpy.props import (BoolProperty)
from bpy.props import (EnumProperty)
from bpy.props import (FloatProperty)



          
class CameraExporter(bpy.types.Operator):
    bl_idname = "object.cameraexporter"   # unique identifier for buttons and menu items to reference.
    bl_label = "Urho3D CameraExport"     # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    sOffset = BoolProperty( name="Save Projection Offset", description="Save Projection Offset Animation", default=True )
    sFov = BoolProperty( name="Save FOV", description="Save FOV Animation", default=False )
    sZoom = BoolProperty( name="Save Zoom", description="Save Zoom Animation", default=True )
    sClip = BoolProperty( name="Save Clip", description="Save Clip Animation", default=False )
        

    interpolation = EnumProperty(
            name = "Interpolation method",
            description = "Set Linear or Spline interpolation",
            items = (('Linear', "Linear", ""),
                     ('Spline',  "Spline", "")),
            default = 'Linear')
            
    wrapmode = EnumProperty(
            name = "Wrap mode",
            description = "",
            items = (('Loop', "Loop", "Loop mode, when the animation arrives to end, it will loop from beginning"),
                     ('Once',  "Once", "Play once mode, when the animation is finished, it will be removed from the object"),
                     ('Clamp', "Clamp", "Clamp mode, when the animation is finished, it will keep the last key frame's value")),
            default = 'Loop')
        
    splineTension = FloatProperty(
        name = "Spline tension", 
        description = "SplineTension", 
        default = 0.7,
        min = 0.0, 
        max = 1.0,
        step = 0.05,
        precision = 1)
        
    speed = FloatProperty(
        name = "Speed", 
        description = "Animation speed", 
        default = 1.0,
        min = 0.0, 
        max = 10.0,
        step = 0.05,
        precision = 1)
                
    def BeginAnimationProperty(self, file, propname):
        if (self.interpolation == 'Spline'):
            file.write('    <attributeanimation name="{0}" interpolationmethod="{1}" splinetension="{2:.2f}" wrapmode="{3}" speed="{4:.2f}"> \n'.format(propname,self.interpolation, self.splineTension, self.wrapmode, self.speed))
        else: 
            file.write('    <attributeanimation name="{0}" interpolationmethod="{1}" wrapmode="{2}" speed="{3:.2f}"> \n'.format(propname,self.interpolation, self.wrapmode, self.speed))
                        
    def EndAnimationProperty(self, file):
        file.write('    </attributeanimation> \n')
        
                
    def SaveCameraAnimation(self, context):
        scene = context.scene;
        selected = context.selected_objects
        i = len(selected)
        print ("selected count:", i)
        print (selected[0].type)
        if (selected[0].type == 'CAMERA'):
            print ("Yes this is camera!")
            cam = bpy.data.cameras[selected[0].name]
            #sx = cam.shift_x
            #sy = cam.shift_y
            
            if (cam.animation_data is not None):
                print ("Camera got animation data!")
                ad = cam.animation_data
                if (ad.action is not None):
                    print ("Camera got action!")
                    a = ad.action
                    print (a.name)
                    print ("frame_range[0]:", a.frame_range[0])
                    print ("frame_range[1]:", a.frame_range[1])
                    fps = scene.render.fps
                    
                    
                    file = open(cam.name + ".xml", 'wt')
                    #file.write("<?xml version="1.0"?>\n")
                    file.write("<Animation>\n")
                        
                    #Save camera shifts
                    if (self.sOffset == True):
                        self.BeginAnimationProperty(file, "Projection Offset")
                        
                        prevValue = ""  
                        for frame in range(int(a.frame_range[0]), int(a.frame_range[1])+1, scene.frame_step):
                            bpy.context.scene.frame_set(frame)
                            bpy.context.scene.update()
                            sx = cam.shift_x
                            sy = cam.shift_y    
                            value = '{0:.3f} {1:.3f}'.format(sx ,sy)
                            if (prevValue not in {value}):
                                file.write('        <keyframe time="{0:.2f}" type="Vector2" value="{1}" />\n'.format( frame / fps, value))
                                prevValue = value
                                
                        self.EndAnimationProperty(file) 
                        
                    #Save camera fov
                    if (self.sFov == True): 
                        self.BeginAnimationProperty(file, "FOV")
                        prevValue = ""
                        for frame in range(int(a.frame_range[0]), int(a.frame_range[1])+1, scene.frame_step):
                            bpy.context.scene.frame_set(frame)
                            bpy.context.scene.update()
                            fov = cam.angle * 57.2958
                            value = '{0:.3f}'.format(fov)
                            if (prevValue not in {value}):
                                file.write('        <keyframe time="{0:.2f}" type="Float" value="{1}" />\n'.format( frame / fps, value))
                                prevValue = value
                                
                        self.EndAnimationProperty(file)
                        
                    #Save camera Zoom
                    if (self.sZoom == True):
                        self.BeginAnimationProperty(file, "Zoom")
                        prevValue = ""
                        for frame in range(int(a.frame_range[0]), int(a.frame_range[1])+1, scene.frame_step):
                        
                            bpy.context.scene.frame_set(frame)
                            bpy.context.scene.update()
                            zoom = 32.0 / cam.sensor_width
                            value = '{0:.3f}'.format(zoom)
                            if (prevValue not in {value}):
                                file.write('        <keyframe time="{0:.2f}" type="Float" value="{1}" />\n'.format( frame / fps, value))
                                prevValue = value
                                
                        self.EndAnimationProperty(file)
                    
                    #Save camera Clip
                    if (self.sClip == True):
                        self.BeginAnimationProperty(file, "Near Clip")
                        prevValue = ""
                        for frame in range(int(a.frame_range[0]), int(a.frame_range[1])+1, scene.frame_step):
                        
                            bpy.context.scene.frame_set(frame)
                            bpy.context.scene.update()
                            clipNear = cam.clip_start
                            value = '{0:.3f}'.format(clipNear)
                            if (prevValue not in {value}):
                                file.write('        <keyframe time="{0:.2f}" type="Float" value="{1}" />\n'.format( frame / fps, value))
                                prevValue = value
                                
                        self.EndAnimationProperty(file)
                        
                        self.BeginAnimationProperty(file, "Far Clip")
                        prevValue = ""
                        for frame in range(int(a.frame_range[0]), int(a.frame_range[1])+1, scene.frame_step):
                        
                            bpy.context.scene.frame_set(frame)
                            bpy.context.scene.update()
                            clipFar = cam.clip_end
                            value = '{0:.3f}'.format(clipFar)
                            if (prevValue not in {value}):
                                file.write('        <keyframe time="{0:.2f}" type="Float" value="{1}" />\n'.format( frame / fps, value))
                                prevValue = value
                                
                        self.EndAnimationProperty(file)
                        
                    file.write("</Animation>")             
                    file.close()        
                      
    def execute(self, context):
        self.SaveCameraAnimation(context)
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(CameraExporter.bl_idname)

def register():
    bpy.utils.register_class(CameraExporter)
    bpy.types.VIEW3D_MT_object.append(menu_func)
    
def unregister():
    bpy.utils.unregister_class(CameraExporter)