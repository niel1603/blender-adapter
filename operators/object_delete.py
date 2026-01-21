import bpy
from blender_adapter.core.app import bl_app

class DeleteObject(bpy.types.Operator):
    bl_idname = "som.delete_object"
    bl_label = "Delete Object"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        session = bl_app().session(scene=context.scene)

        for obj in context.selected_objects:
            if session.runtime.blender.node.get_id(obj):
                return True
            if session.runtime.blender.frame.get_id(obj):
                return True

        return False

    def execute(self, context):
        # 1. SNAPSHOT selection
        objs = list(context.selected_objects)

        # 2. Get live session
        session = bl_app().session(scene=context.scene)

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
        # Delete frames first (they may own nodes)
        for frame_id in frame_ids:
            session.ops.frame.delete(frame_id=frame_id)

        for node_id in node_ids:
            session.ops.node.delete(node_id=node_id)

        return {'FINISHED'}

