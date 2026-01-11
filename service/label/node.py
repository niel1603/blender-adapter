import bpy
import blf
from bpy_extras import view3d_utils

from blender_adapter.service.label.base import AddonService

class NodeLabel(AddonService):
    def __init__(self):
        self._handle = None
        self.font_id = 0
        self.font_size = 12
        self._last_state = None

    def _draw(self):
        context = bpy.context
        scene = context.scene

        # ------------------------------------------------------------------
        # Guard: display state must exist
        # ------------------------------------------------------------------
        display = getattr(scene, "som_display", None)
        if not display:
            return

        # ------------------------------------------------------------------
        # Guard: nothing enabled → nothing to draw
        # ------------------------------------------------------------------
        if not (display.show_node_id or display.show_node_label):
            return

        # ------------------------------------------------------------------
        # Guard: must be in a 3D view region
        # ------------------------------------------------------------------
        region = context.region
        rv3d = context.region_data
        if not region or not rv3d:
            return

        # ------------------------------------------------------------------
        # Helper: semantic node filter (local, explicit)
        # ------------------------------------------------------------------
        def is_node_object(obj):
            rna = getattr(obj, "node_rna", None)
            if not rna:
                return False
            return getattr(rna, "node_type", None) == "Node"

        # ------------------------------------------------------------------
        # Draw labels (NODE OBJECTS ONLY)
        # ------------------------------------------------------------------
        for obj in context.visible_objects:

            if not is_node_object(obj):
                continue

            rna = obj.node_rna
            label_parts = []

            # Only append meaningful values
            if display.show_node_id and rna.node_id:
                label_parts.append(str(rna.node_id))

            if display.show_node_label and rna.label:
                label_parts.append(rna.label)

            # Nothing meaningful → skip
            if not label_parts:
                continue

            coord = view3d_utils.location_3d_to_region_2d(
                region, rv3d, obj.location
            )
            if coord is None:
                continue

            blf.position(self.font_id, coord.x + 8, coord.y + 8, 0)
            blf.size(self.font_id, self.font_size)
            blf.draw(self.font_id, " | ".join(label_parts))


    def _tag_redraw(self, context):
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

    def enable(self):
        if self._handle is None:
            self._handle = bpy.types.SpaceView3D.draw_handler_add(
                self._draw, (), 'WINDOW', 'POST_PIXEL'
            )

    def disable(self):
        if self._handle:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self._handle = None