import bpy
from blender_adapter.core.app import bl_app

class DeleteObject(bpy.types.Operator):
    bl_idname = "som.delete_object"
    bl_label = "Delete Object"
    bl_options = {'REGISTER', 'UNDO'}

    # -------------------------------------------------
    # POLL
    # -------------------------------------------------

    @classmethod
    def poll(cls, context):
        app = bl_app()

        if not context.selected_objects:
            return False

        session = app.get_session(context.scene)
        if session is None:
            return False

        runtime = session.runtime

        for obj in context.selected_objects:
            if runtime.blender.node.get_id(obj):
                return True
            if runtime.blender.frame.get_id(obj):
                return True

        return False

    # -------------------------------------------------
    # EXECUTE
    # -------------------------------------------------

    def execute(self, context):

        # 1. Snapshot selection
        objs = list(context.selected_objects)

        # 2. Get session
        session = bl_app().get_session(scene=context.scene)
        if session is None:
            self.report({'WARNING'}, "Session not started")
            return {'CANCELLED'}

        
        # 3. Resolve IDs
        node_ids: set[str] = set()
        frame_ids: set[str] = set()

        for obj in objs:

            frame_id = session.runtime.blender.frame.get_id(obj)
            if frame_id:
                frame_ids.add(frame_id)
                continue

            node_id = session.runtime.blender.node.get_id(obj)
            if node_id:
                node_ids.add(node_id)

        # 4. TRANSACTION
        for frame_id in frame_ids:
            session.ops.frame.delete(frame_id=frame_id)

        for node_id in node_ids:
            session.ops.node.delete(node_id=node_id)

        return {'FINISHED'}
