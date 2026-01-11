# blender_adapter/service/label/frame_label_service.py

import bpy
import blf
from bpy_extras import view3d_utils

from blender_adapter.service.label.base import AddonService


class FrameLabel(AddonService):
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
        if not (display.show_frame_id or display.show_frame_label):
            return

        # ------------------------------------------------------------------
        # Guard: must be in a 3D view region
        # ------------------------------------------------------------------
        region = context.region
        rv3d = context.region_data
        if not region or not rv3d:
            return

        # ------------------------------------------------------------------
        # Helper: semantic frame filter (local, explicit)
        # ------------------------------------------------------------------
        def is_frame_object(obj):
            rna = getattr(obj, "frame_rna", None)
            if not rna:
                return False
            return getattr(rna, "frame_type", None) == "Frame"

        # ------------------------------------------------------------------
        # Draw labels (FRAME OBJECTS ONLY)
        # ------------------------------------------------------------------
        for obj in context.visible_objects:

            if not is_frame_object(obj):
                continue

            rna = obj.frame_rna
            label_parts = []

            if display.show_frame_id and rna.frame_id:
                label_parts.append(str(rna.frame_id))

            if display.show_frame_label and rna.label:
                label_parts.append(rna.label)

            if not label_parts:
                continue

            # --------------------------------------------------------------
            # Frame position → midpoint of geometry
            # --------------------------------------------------------------
            mesh = obj.data
            if not mesh or len(mesh.vertices) < 2:
                continue

            v0 = obj.matrix_world @ mesh.vertices[0].co
            v1 = obj.matrix_world @ mesh.vertices[1].co
            midpoint = (v0 + v1) * 0.5

            coord = view3d_utils.location_3d_to_region_2d(
                region, rv3d, midpoint
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
