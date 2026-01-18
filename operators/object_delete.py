import bpy
from blender_adapter.core.live import get_live_session

class DeleteObject(bpy.types.Operator):
    bl_idname = "som.delete_object"
    bl_label = "Delete Object"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        session = get_live_session(context)
        for obj in context.selected_objects:
            if session.state.identity.get_node_id_by_object(obj):
                return True
        return False

    def execute(self, context):
        # 1. SNAPSHOT selection
        objs = list(context.selected_objects)

        # 2. Get live session
        session = get_live_session(context)

        # 3. Resolve node IDs (deduplicated)
        node_ids: set[str] = set()
        for obj in objs:
            node_id = session.state.identity.get_node_id_by_object(obj)
            if node_id:
                node_ids.add(node_id)

        # 4. TRANSACTION
        for node_id in node_ids:
            session.ops.nodes.delete(node_id=node_id)

        return {'FINISHED'}


# class DeleteObject(bpy.types.Operator):
#     bl_idname = "som.delete_object"
#     bl_label = "Delete Object"
#     bl_options = {'REGISTER', 'UNDO'}

#     @classmethod
#     def poll(cls, context):
#         return any(
#             BlenderNodeAdapter.get_by_object(obj)
#             or BlenderFrameAdapter.get_by_object(obj)
#             for obj in context.selected_objects
#         )

#     def execute(self, context):
#         # SNAPSHOT selection (important!)
#         objs = list(context.selected_objects)

#         for obj in objs:

#             node = BlenderNodeAdapter.get_by_object(obj)
#             if node:
#                 BlenderNodeAdapter.delete(node)
#                 continue

#             frame = BlenderFrameAdapter.get_by_object(obj)
#             if frame:
#                 BlenderFrameAdapter.delete(frame)

#         return {'FINISHED'}