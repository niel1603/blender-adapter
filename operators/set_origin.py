# operators/op_set_origin_to_geometry.py

import bpy

class SetOriginOperator(bpy.types.Operator):
    """Set origin to geometry for selected objects"""
    bl_idname = "som.set_origin_to_geometry"
    bl_label = "Origin to Geometry"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (
            context.selected_objects is not None
            and len(context.selected_objects) > 0
        )

    def execute(self, context):
        # Blender requires Object Mode for origin ops
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # Apply to all selected objects
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

        self.report({'INFO'}, "Origin set to geometry")
        return {'FINISHED'}
