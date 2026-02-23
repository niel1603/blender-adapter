import bpy
from blender_adapter.core.app import bl_app

class StartSession(bpy.types.Operator):
    bl_idname = "som.start_live_session"
    bl_label = "Start Modeling Session"

    def execute(self, context):
        app = bl_app()
        session = app.start_session(context.scene)
        session.ensure_ready()

        self.report({'INFO'}, "SoM session started")
        return {'FINISHED'}