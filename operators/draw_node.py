# blender_adapter/operators/node.py

import bpy
from blender_adapter.crud.node import BlenderNodeAdapter
from blender_adapter.service.snapping import SnappingService
from blender_adapter.utils.navigation import is_navigation_event

class DrawNode(bpy.types.Operator):
    bl_idname = "som.create_node_modal"
    bl_label = "Draw Node"
    bl_options = {'REGISTER', 'UNDO'}

    snap_threshold: bpy.props.FloatProperty(default=10.0)  # type: ignore
    empty_size: bpy.props.FloatProperty(default=0.1, min=0.001)  # type: ignore

    def invoke(self, context, event):
        if context.area.type != 'VIEW_3D':
            self.report({'WARNING'}, "3D View required")
            return {'CANCELLED'}

        self._snapping = SnappingService(self.snap_threshold)

        context.area.header_text_set(
            "Click to place Node | Shift+Click to snap"
        )
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):

        if is_navigation_event(event):
            return {'PASS_THROUGH'}

        if event.type == 'ESC':
            context.area.header_text_set(None)
            return {'CANCELLED'}

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            point = self._snapping.get_point(context, event)

            node = BlenderNodeAdapter.create(
                location=point,
                size=self.empty_size,
                collection=context.collection,
            )
            node.select(context)

        return {'RUNNING_MODAL'}
