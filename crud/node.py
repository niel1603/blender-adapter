# blender_adapter/crud/node.py

import bpy
from mathutils import Vector
from blender_adapter.core.node import BlenderNode

class BlenderNodeAdapter:

    # ---------- ID ----------
    @staticmethod
    def next_id(prefix="N"):
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
        location,
        size: float = 0.5,
        collection=None,
    ) -> BlenderNode:

        if collection is None:
            collection = bpy.context.scene.collection

        node_id, name = BlenderNodeAdapter.next_id("N")

        obj = bpy.data.objects.new(name, None)
        obj.empty_display_type = 'PLAIN_AXES'
        obj.empty_display_size = size
        obj.location = location
        collection.objects.link(obj)

        rna = obj.node_rna
        rna.node_id = node_id
        rna.node_type = BlenderNode.TYPE   # 🔒 enforced
        rna.label = name

        return BlenderNode(obj)

    # ---------- MOVE ----------
    @staticmethod
    def move(node: BlenderNode, direction):
        node.obj.location += Vector(direction)

    # ---------- SET LOCATION (used by drag) ----------
    @staticmethod
    def set_location(node: BlenderNode, location):
        node.obj.location = location

    # ---------- DELETE ----------
    @staticmethod
    def delete(node: BlenderNode):
        bpy.data.objects.remove(node.obj, do_unlink=True)

    # ---------- REPLICATE ----------
    @staticmethod
    def replicate(
        node: BlenderNode,
        *,
        location=None,
        collection=None,
    ) -> BlenderNode:

        src = node.obj

        if location is None:
            location = src.location.copy()

        if collection is None:
            collection = src.users_collection[0]

        node_id, name = BlenderNodeAdapter.next_id("N")

        obj = bpy.data.objects.new(name, None)
        obj.empty_display_type = src.empty_display_type
        obj.empty_display_size = src.empty_display_size
        obj.location = location
        collection.objects.link(obj)

        rna = obj.node_rna
        rna.node_id = node_id
        rna.node_type = BlenderNode.TYPE   # 🔒 enforced
        rna.label = name

        return BlenderNode(obj)

    # ---------- READ (single) ----------

    @staticmethod
    def get_by_id(node_id: str) -> BlenderNode | None:
        for obj in bpy.data.objects:
            if (
                hasattr(obj, "node_rna")
                and obj.node_rna.node_type == BlenderNode.TYPE
                and obj.node_rna.node_id == node_id
            ):
                return BlenderNode(obj)
        return None

    @staticmethod
    def get_by_object(obj: bpy.types.Object) -> BlenderNode | None:
        try:
            return BlenderNode(obj)
        except TypeError:
            return None

    # ---------- READ (collection) ----------

    @staticmethod
    def all() -> list[BlenderNode]:
        result: list[BlenderNode] = []

        for obj in bpy.data.objects:
            if (
                hasattr(obj, "node_rna")
                and obj.node_rna.node_type == BlenderNode.TYPE
            ):
                result.append(BlenderNode(obj))

        return result

    @staticmethod
    def selected(context) -> list[BlenderNode]:
        result: list[BlenderNode] = []

        for obj in context.selected_objects:
            if (
                hasattr(obj, "node_rna")
                and obj.node_rna.node_type == BlenderNode.TYPE
            ):
                result.append(BlenderNode(obj))

        return result

    # ---------- QUERY ----------

    @staticmethod
    def exists(node_id: str) -> bool:
        return BlenderNodeAdapter.get_by_id(node_id) is not None