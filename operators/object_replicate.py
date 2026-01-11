import bpy
from mathutils import Vector

from blender_adapter.crud.node import BlenderNodeAdapter
from blender_adapter.crud.frame import BlenderFrameAdapter

class ReplicateObject(bpy.types.Operator):
    bl_idname = "som.replicate_object"
    bl_label = "Replicate Object"
    bl_options = {'REGISTER', 'UNDO'}

    dx: bpy.props.FloatProperty(name="ΔX", default=0.0, options={'SKIP_SAVE'})  # type: ignore
    dy: bpy.props.FloatProperty(name="ΔY", default=0.0, options={'SKIP_SAVE'})  # type: ignore
    dz: bpy.props.FloatProperty(name="ΔZ", default=0.0, options={'SKIP_SAVE'})  # type: ignore

    count: bpy.props.IntProperty(
        name="Count",
        default=1,
        min=1,
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        return any(
            BlenderNodeAdapter.get_by_object(obj)
            or BlenderFrameAdapter.get_by_object(obj)
            for obj in context.selected_objects
        )

    def execute(self, context):
        delta = Vector((self.dx, self.dy, self.dz))

        # SNAPSHOT selection (important!)
        source_objs = list(context.selected_objects)
        new_objs = []

        # BREADTH-FIRST replication (by step)
        for i in range(1, self.count + 1):
            step_delta = delta * i

            for obj in source_objs:

                node = BlenderNodeAdapter.get_by_object(obj)
                if node:
                    new_node = BlenderNodeAdapter.replicate(
                        node,
                        location=node.obj.location + step_delta,
                    )
                    new_objs.append(new_node.obj)
                    continue

                frame = BlenderFrameAdapter.get_by_object(obj)
                if frame:
                    new_frame = BlenderFrameAdapter.replicate(
                        frame,
                        direction=step_delta,
                    )
                    new_objs.append(new_frame.obj)

        # ----- selection handling -----
        for obj in new_objs:
            obj.select_set(True)

        if new_objs:
            context.view_layer.objects.active = new_objs[-1]

        return {'FINISHED'}
