import bpy

from blender_adapter.crud.node import BlenderNodeAdapter
from blender_adapter.crud.frame import BlenderFrameAdapter

class DeleteObject(bpy.types.Operator):
    bl_idname = "som.delete_object"
    bl_label = "Delete Object"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return any(
            BlenderNodeAdapter.get_by_object(obj)
            or BlenderFrameAdapter.get_by_object(obj)
            for obj in context.selected_objects
        )

    def execute(self, context):
        # SNAPSHOT selection (important!)
        objs = list(context.selected_objects)

        for obj in objs:

            node = BlenderNodeAdapter.get_by_object(obj)
            if node:
                BlenderNodeAdapter.delete(node)
                continue

            frame = BlenderFrameAdapter.get_by_object(obj)
            if frame:
                BlenderFrameAdapter.delete(frame)

        return {'FINISHED'}


