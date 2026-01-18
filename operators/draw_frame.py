import bpy
from blender_adapter.service.snapping import SnappingService
from blender_adapter.utils.navigation import is_navigation_event
from blender_adapter.core.app import bl_app

class DrawFrame(bpy.types.Operator):
    bl_idname = "som.create_frame_modal"
    bl_label = "Draw Frame"
    bl_options = {'REGISTER', 'UNDO'}

    snap_threshold: bpy.props.FloatProperty(default=10.0)  # type: ignore
    empty_size: bpy.props.FloatProperty(default=0.1, min=0.001)  # type: ignore

    def invoke(self, context, event):
        if context.area.type != 'VIEW_3D':
            self.report({'WARNING'}, "3D View required")
            return {'CANCELLED'}

        self._snapping = SnappingService(self.snap_threshold)
        self._start_node_id: str | None = None

        context.area.header_text_set(
            "Click start node | Shift+Click to snap"
        )
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):

        if is_navigation_event(event):
            return {'PASS_THROUGH'}

        if event.type == 'ESC':
            self._start_node_id = None
            context.area.header_text_set(None)
            return {'CANCELLED'}

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':

            # 1. Resolve intent (UI)
            point = self._snapping.get_point(context, event)

            # 2. Get live session
            session = bl_app().session(scene=context.scene)

            # 3. Always create/reuse node through txn
            # --- resolve / reuse node at click location ---
            bl_node = session.ops.nodes.get_or_create(
                location=point,
                size=self.empty_size,
            )

            node_id = bl_node.id

            # --- no start or end node yet → set start or end ---
            if self._start_node_id is None:
                self._start_node_id = node_id
                bl_node.select(context)

                context.area.header_text_set(
                    "Start node set — click end node"
                )
                return {'RUNNING_MODAL'}

            # --- start or end node already set → attempt to create frame ---
            if node_id == self._start_node_id:
                self.report({'WARNING'}, "Cannot create frame to same node")
                return {'RUNNING_MODAL'}

            # 4. Commit frame via transaction
            bl_frame = session.ops.frames.create(
                n1_id=self._start_node_id,
                n2_id=node_id,
            )

            # 5. UI feedback
            bl_frame.select(context)

            # 6. Continue chaining
            self._start_node_id = node_id
            context.area.header_text_set(
                "Frame created — click to continue"
            )

        return {'RUNNING_MODAL'}
