import mathutils
from bpy_extras import view3d_utils

from blender_adapter.crud.node import BlenderNodeAdapter
from blender_adapter.crud.frame import BlenderFrameAdapter

from blender_adapter.utils.is_object import is_plain_empty, is_plain_mesh

# ---------- SNAP PROVIDERS ----------
def snap_plain_empty_origin(obj):
    """
    Snap to EMPTY object origin (non-node)
    """
    if not is_plain_empty(obj):
        return

    yield obj.matrix_world.translation

def snap_plain_mesh_endpoints(obj):
    """
    Snap to mesh extreme vertices (non-frame)
    """
    if not is_plain_mesh(obj):
        return

    mesh = obj.data
    if not mesh.vertices:
        return

    # world-space vertices
    verts = [obj.matrix_world @ v.co for v in mesh.vertices]

    # choose extremes (bounding box corners approximation)
    min_v = min(verts, key=lambda v: (v.x, v.y, v.z))
    max_v = max(verts, key=lambda v: (v.x, v.y, v.z))

    yield min_v
    yield max_v

def snap_plain_mesh_midpoint(obj):
    """
    Snap to mesh bounding-box center (non-frame)
    """
    if not is_plain_mesh(obj):
        return

    mesh = obj.data
    if not mesh.vertices:
        return

    verts = [obj.matrix_world @ v.co for v in mesh.vertices]

    center = sum(verts, mathutils.Vector()) / len(verts)
    yield center

def snap_node_points(obj):
    """
    Snap to node origins
    """
    node = BlenderNodeAdapter.get_by_object(obj)
    if not node:
        return

    yield node.obj.matrix_world.translation

def snap_frame_endpoints(obj):
    """
    Snap to frame start & end points
    """
    frame = BlenderFrameAdapter.get_by_object(obj)
    if not frame:
        return

    mesh = frame.obj.data
    if not mesh or len(mesh.vertices) < 2:
        return

    yield frame.obj.matrix_world @ mesh.vertices[0].co
    yield frame.obj.matrix_world @ mesh.vertices[1].co

def snap_frame_midpoint(obj):
    """
    Snap to frame midpoint
    """
    frame = BlenderFrameAdapter.get_by_object(obj)
    if not frame:
        return

    mesh = frame.obj.data
    if not mesh or len(mesh.vertices) < 2:
        return

    v0 = frame.obj.matrix_world @ mesh.vertices[0].co
    v1 = frame.obj.matrix_world @ mesh.vertices[1].co
    yield (v0 + v1) * 0.5

# Central registry (order matters)
SNAP_PROVIDERS = [
    # ---- domain-aware ----
    snap_node_points,
    snap_frame_endpoints,
    snap_frame_midpoint,

    # ---- generic objects ----
    snap_plain_empty_origin,
    snap_plain_mesh_endpoints,
    snap_plain_mesh_midpoint,
]

class SnappingService:
    """
    Decides the correct 3D point from mouse input,
    considering snapping rules.
    """

    def __init__(self, snap_threshold: float = 10.0):
        self.snap_threshold = snap_threshold

    # ---------- public API ----------

    def get_point(self, context, event):
        if self.should_snap(event):
            return self._get_snapped_point(context, event)
        return self._get_free_point(context, event)

    # ---------- policy ----------

    def should_snap(self, event) -> bool:
        """
        Define snapping modifier policy.
        Currently: Shift = snap
        """
        return event.shift

    # ---------- free placement ----------

    def _get_free_point(self, context, event):
        region = context.region
        rv3d = context.region_data
        coord = (event.mouse_region_x, event.mouse_region_y)
        depth = context.scene.cursor.location

        return view3d_utils.region_2d_to_location_3d(
            region, rv3d, coord, depth
        )

    # ---------- snapping ----------

    def _get_snapped_point(self, context, event):
        region = context.region
        rv3d = context.region_data
        mouse = mathutils.Vector(
            (event.mouse_region_x, event.mouse_region_y)
        )

        best = None  # (world_co, dist)

        def consider(world_co):
            nonlocal best
            screen_co = view3d_utils.location_3d_to_region_2d(
                region, rv3d, world_co
            )
            if screen_co is None:
                return

            dist = (mouse - screen_co).length
            if dist < self.snap_threshold and (
                best is None or dist < best[1]
            ):
                best = (world_co, dist)

        for obj in context.scene.objects:
            for provider in SNAP_PROVIDERS:
                for world_co in provider(obj):
                    consider(world_co)

        if best:
            return best[0]

        return self._get_free_point(context, event)
