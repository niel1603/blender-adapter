from collections.abc import Iterator
import bpy
from mathutils import Vector
from blender_adapter.core.object import BlFrameWrap

class BlFrameObj:
    """
    Blender frame APIs
    """

    def __init__(self):
        self._frames: dict[str, str] = {}  # frame_id -> object name

    # ---------- rebuild ----------

    def rebuild(self, scene: bpy.types.Scene):
        """
        Rebuild frame references from Blender scene.
        """
        self._frames.clear()

        for obj in scene.objects:
            if not hasattr(obj, "frame_rna"):
                continue

            frame_id = obj.frame_rna.frame_id
            if frame_id:
                self._frames[frame_id] = obj.name

    # ---------- clear ----------

    def clear(self):
        """
        Remove all Blender frame objects managed by this container.
        Idempotent and defensive.
        """
        for name in list(self._frames.values()):
            obj = bpy.data.objects.get(name)
            if obj:
                bpy.data.objects.remove(obj, do_unlink=True)

        self._frames.clear()

    # ---------- access ----------

    def __len__(self) -> int:
        return len(self._frames)

    def __contains__(self, frame_id: str) -> bool:
        return frame_id in self._frames

    def __getitem__(self, frame_id: str) -> BlFrameWrap:
        frame = self.get(frame_id)
        if frame is None:
            raise KeyError(f"Blender frame '{frame_id}' not found or invalid")
        return frame

    def __iter__(self) -> Iterator[BlFrameWrap]:
        """
        Iterate over *valid* Blender frames.
        Invalid ones are skipped safely.
        """
        for frame_id in tuple(self._frames):
            frame = self.get(frame_id)
            if frame:
                yield frame

    def get(
        self,
        frame_id: str,
        default: BlFrameWrap | None = None,
    ) -> BlFrameWrap | None:
        name = self._frames.get(frame_id)
        if not name:
            return default

        obj = bpy.data.objects.get(name)
        if obj is None or not hasattr(obj, "frame_rna"):
            return default

        return BlFrameWrap(obj)

    def items(self):
        """
        Iterate over (frame_id, BlFrameWrap) pairs.
        Invalid frames are skipped.
        """
        for frame_id in tuple(self._frames):
            frame = self.get(frame_id)
            if frame:
                yield frame_id, frame

    def values(self):
        """
        Iterate over valid BlFrameWrap objects.
        """
        return iter(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({len(self)} refs)"

    # ---------- reverse lookup ----------

    def get_id(self, obj: bpy.types.Object) -> str | None:
        if not hasattr(obj, "frame_rna"):
            return None

        frame_id = obj.frame_rna.frame_id
        if frame_id in self._frames:
            return frame_id

        return None

    # ---------- creation ----------

    def _center_geometry(self, obj):
        mesh = obj.data
        if not mesh.vertices:
            return

        center = Vector()
        for v in mesh.vertices:
            center += v.co
        center /= len(mesh.vertices)

        for v in mesh.vertices:
            v.co -= center

        obj.location += obj.matrix_world.to_3x3() @ center

    def create(
        self,
        *,
        frame_id: str,
        name: str,
        start,
        end,
        start_node_id: str,
        end_node_id: str,
        collection=None,
    ) -> BlFrameWrap:
        """
        Create a Blender-backed frame.
        """

        # uniqueness enforcement
        if frame_id in self._frames:
            raise RuntimeError(f"Duplicate frame_id '{frame_id}'")

        # collection resolution
        if collection is None:
            collection = bpy.context.scene.collection

        # Blender object creation
        mesh = bpy.data.meshes.new(f"{name}_mesh")
        mesh.from_pydata([start, end], [(0, 1)], [])
        mesh.update()

        obj = bpy.data.objects.new(name, mesh)
        collection.objects.link(obj)

        self._center_geometry(obj)

        # RNA binding
        rna = obj.frame_rna
        rna.frame_id = frame_id
        rna.start_node = start_node_id
        rna.end_node = end_node_id
        rna.label = name

       # bookkeeping
        self._frames[frame_id] = obj.name
        return BlFrameWrap(obj)

    # ---------- mutation (visual only) ----------

    def move(
            self, 
            frame: BlFrameWrap, 
            start_node_id: str,
            end_node_id: str,
            direction,
            ):
        """
        Move Blender frame object visually.
        Topology must already be updated in FrameObj.
        """
        rna = frame.obj.frame_rna
        rna.start_node = start_node_id
        rna.end_node = end_node_id
        
        frame.obj.location += Vector(direction)

    def set_location(
            self, 
            frame: BlFrameWrap, 
            start_node_id: str,
            end_node_id: str,
            location,
            ):
        
        rna = frame.obj.frame_rna
        rna.start_node = start_node_id
        rna.end_node = end_node_id
    
        frame.obj.location = location

    # ---------- deletion ----------

    def delete(self, frame: BlFrameWrap):
        frame_id = frame.id
        bpy.data.objects.remove(frame.obj, do_unlink=True)
        self._frames.pop(frame_id, None)

    # ---------- replicate ----------

    def replicate_from(
        self,
        *,
        src: BlFrameWrap,
        frame_id: str,
        name: str,
        start,
        end,
        start_node_id: str,
        end_node_id: str,
        collection=None,
    ) -> BlFrameWrap:
        """
        Strict replicate from an existing Blender frame.
        """

        # uniqueness enforcement
        if frame_id in self._frames:
            raise RuntimeError(f"Duplicate frame_id '{frame_id}'")
        
        src_obj = src.obj

        # collection resolution
        if collection is None:
            collection = src_obj.users_collection[0]

        # Blender object replicate from src
        obj = bpy.data.objects.new(name, src_obj.data)
        mesh = obj.data
        mesh.clear_geometry()
        mesh.from_pydata([start, end], [(0, 1)], [])
        mesh.update()
        collection.objects.link(obj)

        self._center_geometry(obj)

        # RNA binding
        rna = obj.frame_rna
        rna.frame_id = frame_id
        rna.start_node = start_node_id
        rna.end_node = end_node_id
        rna.label = name

       # bookkeeping
        self._frames[frame_id] = obj.name
        return BlFrameWrap(obj)
