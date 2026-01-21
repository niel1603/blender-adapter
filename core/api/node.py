from collections.abc import Iterator
import bpy
from mathutils import Vector
from blender_adapter.core.object import BlNodeWrap

class BlNodeObj:
    """
    Blender node APIs
    """

    def __init__(self):
        self._nodes: dict[str, str] = {}  # node_id -> object name

    # ---------- rebuild ----------

    def rebuild(self, scene: bpy.types.Scene):
        self._nodes.clear()

        for obj in scene.objects:
            if not hasattr(obj, "node_rna"):
                continue

            node_id = obj.node_rna.node_id
            if node_id:
                self._nodes[node_id] = obj.name

    # ---------- clear ----------

    def clear(self):
        """
        Remove all Blender node objects managed by this container.
        Idempotent and defensive.
        """
        for name in list(self._nodes.values()):
            obj = bpy.data.objects.get(name)
            if obj:
                bpy.data.objects.remove(obj, do_unlink=True)

        self._nodes.clear()

    # ---------- access ----------

    def __len__(self) -> int:
        return len(self._nodes)

    def __contains__(self, node_id: str) -> bool:
        return node_id in self._nodes

    def __getitem__(self, node_id: str) -> BlNodeWrap:
        node = self.get(node_id)
        if node is None:
            raise KeyError(f"Blender node '{node_id}' not found or invalid")
        return node

    def __iter__(self) -> Iterator[BlNodeWrap]:
        """
        Iterate over *valid* Blender nodes.
        Invalid ones are skipped safely.
        """
        for node_id in tuple(self._nodes):
            node = self.get(node_id)
            if node:
                yield node

    def get(self, node_id: str, default: BlNodeWrap | None = None) -> BlNodeWrap | None:
        name = self._nodes.get(node_id)
        if not name:
            return default

        obj = bpy.data.objects.get(name)
        if obj is None or not hasattr(obj, "node_rna"):
            return default

        return BlNodeWrap(obj)

    def items(self):
        """
        Iterate over (node_id, BlNodeWrap) pairs.
        Invalid nodes are skipped.
        """
        for node_id in tuple(self._nodes):
            node = self.get(node_id)
            if node:
                yield node_id, node

    def values(self):
        """
        Iterate over valid BlNodeWrap objects.
        """
        return iter(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({len(self)} refs)"

    # ---------- reverse lookup ----------

    def get_id(self, obj: bpy.types.Object) -> str | None:
        if not hasattr(obj, "node_rna"):
            return None

        node_id = obj.node_rna.node_id
        if node_id in self._nodes:
            return node_id

        return None

    # ---------- creation ----------

    def create(
        self,
        *,
        node_id: str,
        name: str,
        location,
        size: float = 0.1,
        collection=None,
    ) -> BlNodeWrap:
        """
        Create a Blender-backed node.
        """

        # uniqueness enforcement
        if node_id in self._nodes:
            raise RuntimeError(f"Duplicate node_id '{node_id}'")

        # collection resolution
        if collection is None:
            collection = bpy.context.scene.collection

        # Blender object creation
        obj = bpy.data.objects.new(name, None)
        obj.empty_display_type = 'PLAIN_AXES'
        obj.empty_display_size = size
        obj.location = location

        collection.objects.link(obj)

        # RNA binding
        rna = obj.node_rna
        rna.node_id = node_id
        rna.label = name

        # bookkeeping
        self._nodes[node_id] = obj.name

        return BlNodeWrap(obj)
    
    # ---------- mutation ----------

    def move(self, node: BlNodeWrap, direction):
        node.obj.location += Vector(direction)

    def set_location(self, node: BlNodeWrap, location):
        node.obj.location = location
    
    # ---------- deletion ----------

    def delete(self, node: BlNodeWrap):
        node_id = node.id
        bpy.data.objects.remove(node.obj, do_unlink=True)
        self._nodes.pop(node_id, None)

    # ---------- replicate ----------

    def replicate_from(
        self,
        *,
        src: BlNodeWrap,
        node_id: str,
        name: str,
        location,
        collection=None,
    ) -> BlNodeWrap:
        """
        Strict replicate from an existing Blender node.
        """

        if node_id in self._nodes:
            raise RuntimeError(f"Duplicate node_id '{node_id}'")

        src_obj = src.obj

        if collection is None:
            collection = src_obj.users_collection[0]

        obj = bpy.data.objects.new(name, None)
        obj.empty_display_type = src_obj.empty_display_type
        obj.empty_display_size = src_obj.empty_display_size
        obj.location = location

        collection.objects.link(obj)

        rna = obj.node_rna
        rna.node_id = node_id
        rna.label = name

        self._nodes[node_id] = obj.name
        return BlNodeWrap(obj)
