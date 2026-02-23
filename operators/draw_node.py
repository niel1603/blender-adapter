# blender_adapter/operators/node.py

import bpy
from blender_adapter.service.snapping import SnappingService
from blender_adapter.utils.navigation import is_navigation_event
from blender_adapter.core.app import bl_app

class DrawNode(bpy.types.Operator):
    bl_idname = "som.create_node_modal"
    bl_label = "Draw Node"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        if context.area.type != 'VIEW_3D':
            self.report({'WARNING'}, "3D View required")
            return {'CANCELLED'}

        self._snapping = SnappingService()

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

            # 1. Get live session (creates if needed)
            session = bl_app().get_session(scene=context.scene)
            if session is None:
                self.report({'WARNING'}, "Session not started")
                return {'CANCELLED'}

            # 2. Resolve intent (UI / interaction)
            point = self._snapping.get_point(context, event)

            # 3. Commit through manager (TRANSACTION)
            bl_node = session.ops.node.create(location=point)

            # 4. UI feedback
            bl_node.select(context)

        return {'RUNNING_MODAL'}
    