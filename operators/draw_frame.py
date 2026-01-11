import bpy
from blender_adapter.crud.frame import BlenderFrameAdapter
from blender_adapter.service.snapping import SnappingService
from blender_adapter.utils.navigation import is_navigation_event

class DrawFrame(bpy.types.Operator):
    bl_idname = "som.create_frame_modal"
    bl_label = "Draw Frame"
    bl_options = {'REGISTER', 'UNDO'}

    snap_threshold: bpy.props.FloatProperty(default=10.0)  # type: ignore

    def invoke(self, context, event):
        if context.area.type != 'VIEW_3D':
            self.report({'WARNING'}, "3D View required")
            return {'CANCELLED'}

        self._snapping = SnappingService(self.snap_threshold)
        self._start_point = None
        self._start_node_id = None

        context.area.header_text_set(
            "Click start point | Shift+Click to snap"
        )
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):

        if is_navigation_event(event):
            return {'PASS_THROUGH'}

        if event.type == 'ESC':
            self._start_point = None
            self._start_node_id = None
            context.area.header_text_set(None)
            return {'CANCELLED'}

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            point = self._snapping.get_point(context, event)

            if self._start_point is None:
                self._start_point = point
                self._start_node_id = "TEMP"  # placeholder for now
                context.area.header_text_set(
                    "Start point set — click end point"
                )
                return {'RUNNING_MODAL'}

            frame = BlenderFrameAdapter.create(
                start=self._start_point,
                end=point,
                start_node_id=self._start_node_id,
                end_node_id="TEMP",
                collection=context.collection,
            )
            frame.select(context)

            self._start_point = point
            self._start_node_id = "TEMP"
            context.area.header_text_set(
                "Frame created — click to continue"
            )

        return {'RUNNING_MODAL'}
