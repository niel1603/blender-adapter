# blender_adapter/crud/frame.py

import bpy
from blender_adapter.core.frame import BlenderFrame
from mathutils import Vector

class BlenderFrameAdapter:

    # ---------- ID ----------
    @staticmethod
    def next_id(prefix="F"):
        max_index = 0
        for obj in bpy.data.objects:
            if obj.name.startswith(prefix):
                suffix = obj.name[len(prefix):]
                if suffix.isdigit():
                    max_index = max(max_index, int(suffix))
        idx = max_index + 1
        return str(idx), f"{prefix}{idx}"

    # ---------- CREATE ----------
    @staticmethod
    def create(
        *,
        start,
        end,
        start_node_id: str,
        end_node_id: str,
        collection=None,
    ) -> BlenderFrame:

        if collection is None:
            collection = bpy.context.scene.collection

        frame_id, name = BlenderFrameAdapter.next_id("F")

        mesh = bpy.data.meshes.new(f"{name}_Mesh")
        mesh.from_pydata([start, end], [(0, 1)], [])
        mesh.update()

        obj = bpy.data.objects.new(name, mesh)
        collection.objects.link(obj)

        BlenderFrameAdapter._center_geometry(obj)

        rna = obj.frame_rna
        rna.frame_id = frame_id
        rna.frame_type = BlenderFrame.TYPE   # 🔒 enforced
        rna.start_node = start_node_id
        rna.end_node = end_node_id
        rna.label = name

        return BlenderFrame(obj)

    # ---------- GEOMETRY ----------
    @staticmethod
    def _center_geometry(obj):
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

    # ---------- MOVE ----------
    @staticmethod
    def move(frame: BlenderFrame, direction):
        frame.obj.location += Vector(direction)

    # ---------- DELETE ----------
    @staticmethod
    def delete(frame: BlenderFrame):
        bpy.data.objects.remove(frame.obj, do_unlink=True)

    # ---------- REPLICATE ----------
    @staticmethod
    def replicate(
        frame: BlenderFrame,
        *,
        direction=(0, 0, 0),
        collection=None,
    ) -> BlenderFrame:

        src = frame.obj

        if collection is None:
            collection = src.users_collection[0]

        frame_id, name = BlenderFrameAdapter.next_id("F")

        new_obj = src.copy()
        new_obj.data = src.data.copy()
        new_obj.name = name
        new_obj.location = src.location + Vector(direction)

        collection.objects.link(new_obj)

        rna = new_obj.frame_rna
        rna.frame_id = frame_id
        rna.frame_type = BlenderFrame.TYPE   # 🔒 enforced
        rna.start_node = src.frame_rna.start_node
        rna.end_node = src.frame_rna.end_node
        rna.label = name

        return BlenderFrame(new_obj)

    # ---------- READ (single) ----------

    @staticmethod
    def get_by_id(frame_id: str) -> BlenderFrame | None:
        for obj in bpy.data.objects:
            if (
                hasattr(obj, "frame_rna")
                and obj.frame_rna.frame_type == BlenderFrame.TYPE
                and obj.frame_rna.frame_id == frame_id
            ):
                return BlenderFrame(obj)
        return None

    @staticmethod
    def get_by_object(obj: bpy.types.Object) -> BlenderFrame | None:
        try:
            return BlenderFrame(obj)
        except TypeError:
            return None

    # ---------- READ (collection) ----------

    @staticmethod
    def all() -> list[BlenderFrame]:
        result: list[BlenderFrame] = []

        for obj in bpy.data.objects:
            if (
                hasattr(obj, "frame_rna")
                and obj.frame_rna.frame_type == BlenderFrame.TYPE
            ):
                result.append(BlenderFrame(obj))

        return result

    @staticmethod
    def selected(context) -> list[BlenderFrame]:
        result: list[BlenderFrame] = []

        for obj in context.selected_objects:
            if (
                hasattr(obj, "frame_rna")
                and obj.frame_rna.frame_type == BlenderFrame.TYPE
            ):
                result.append(BlenderFrame(obj))

        return result

    # ---------- QUERY ----------

    @staticmethod
    def exists(frame_id: str) -> bool:
        return BlenderFrameAdapter.get_by_id(frame_id) is not None