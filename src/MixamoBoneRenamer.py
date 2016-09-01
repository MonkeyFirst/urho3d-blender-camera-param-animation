bl_info = {
    "name": "Mixamo Bone Renamer for Urho3D",
    "author": "codingmonkey",
    "category": "Object",
    "blender": (2, 77, 0)   
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



          
class MixamoBoneRenamer(bpy.types.Operator):
    bl_idname = "object.mixamobonerenamer"   # unique identifier for buttons and menu items to reference.
    bl_label = "Urho3D MixamoBoneRenamer"     # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.
    
    mixamoPrefix = "mixamorig:"
    rightPrefix = "Right"
    leflPrefix = "Left"
    
    def RenameBones(self, context):
        scene = context.scene;
        selected = context.selected_objects
        i = len(selected)
        print ("selected count:", i)
        print (selected[0].type)
        if (selected[0].type == 'ARMATURE'):
            print ("Has ARMA!")
            
            for bone in selected[0].data.bones:
                #print ("Omnited " + self.omnitPref(bone.name)) 
                omnited = self.omnitPref(bone.name)
                lpref = self.checkoutForLeft(omnited)
                rpref = self.checkoutForRight(lpref)
                print ("RENAME BONE " + bone.name + "  TO  " + rpref)                
                bone.name = rpref
            
            pass
        
    def omnitPref(self, boneName):
        if boneName.startswith(self.mixamoPrefix):
            pl = len(self.mixamoPrefix)
            return boneName[pl:]
        
        return boneName  
    
    def checkoutForLeft(self, boneName):
        if boneName.startswith(self.leflPrefix):
            ll = len(self.leflPrefix)
            wl = boneName[ll:]
            return wl+".L"
        
        return boneName  
    
    def checkoutForRight(self, boneName):
        if boneName.startswith(self.rightPrefix):
            rl = len(self.rightPrefix)
            wr = boneName[rl:]
            return wr+".R"
        
        return boneName  
        
    
                      
    def execute(self, context):
        self.RenameBones(context)
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(MixamoBoneRenamer.bl_idname)

def register():
    bpy.utils.register_class(MixamoBoneRenamer)
    bpy.types.VIEW3D_MT_object.append(menu_func)
    
def unregister():
    bpy.utils.unregister_class(MixamoBoneRenamer)
    
if __name__ == "__main__":
    register()

    # test call
    bpy.ops.object.mixamobonerenamer()
