import bpy
from blender_adapter.core.live import get_live_session

class StartSession(bpy.types.Operator):
    bl_idname = "som.start_live_session"
    bl_label = "Start Modeling Session"

    def execute(self, context):
        get_live_session(context)
        self.report({'INFO'}, "SoM session started")
        return {'FINISHED'}
