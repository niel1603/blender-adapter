import bpy

from blender_adapter.crud.node import BlenderNodeAdapter
from blender_adapter.crud.frame import BlenderFrameAdapter

class MoveObject(bpy.types.Operator):
    bl_idname = "som.move_object"
    bl_label = "Move Object"
    bl_options = {'REGISTER', 'UNDO'}

    dx: bpy.props.FloatProperty(name="ΔX", default=0.0, options={'SKIP_SAVE'})  # type: ignore
    dy: bpy.props.FloatProperty(name="ΔY", default=0.0, options={'SKIP_SAVE'})  # type: ignore
    dz: bpy.props.FloatProperty(name="ΔZ", default=0.0, options={'SKIP_SAVE'})  # type: ignore

    @classmethod
    def poll(cls, context):
        return any(
            BlenderNodeAdapter.get_by_object(obj)
            or BlenderFrameAdapter.get_by_object(obj)
            for obj in context.selected_objects
        )

    def execute(self, context):
        direction = (self.dx, self.dy, self.dz)

        # snapshot selection
        for obj in list(context.selected_objects):

            node = BlenderNodeAdapter.get_by_object(obj)
            if node:
                BlenderNodeAdapter.move(node, direction)
                continue

            frame = BlenderFrameAdapter.get_by_object(obj)
            if frame:
                BlenderFrameAdapter.move(frame, direction)

        return {'FINISHED'}
