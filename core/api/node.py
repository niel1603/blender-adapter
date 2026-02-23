from collections.abc import Iterator
import bpy

from structural_om.core.object import Node
from structural_om.core.api.node import NodeObj
from blender_adapter.core.object import BlNodeWrap

class BlNodeObj:

    def __init__(self, domain: NodeObj):
        self.domain = domain
        self._nodes: dict[str, str] = {}  # node_id → object name

    # ---------- rebuild from scene api ----------

    def extract_from_scene(self, scene):

        extracted = []

        for obj in scene.objects:
            if hasattr(obj, "node_rna") and obj.node_rna.node_id:
                extracted.append(
                    (obj.node_rna.node_id, tuple(obj.location))
                )

        return extracted
    
    def rebuild_identity_from_scene(self, scene):

        self._nodes.clear()

        for obj in scene.objects:
            if hasattr(obj, "node_rna") and obj.node_rna.node_id:
                node_id = obj.node_rna.node_id
                self._nodes[node_id] = obj.name
    
    def sync_from_domain(self):

        # Remove stale objects
        for node_id in list(self._nodes):
            if node_id not in self.domain:
                name = self._nodes.pop(node_id)
                obj = bpy.data.objects.get(name)
                if obj:
                    bpy.data.objects.remove(obj, do_unlink=True)

        # Create missing objects
        for node in self.domain:
            if node.id not in self._nodes:
                self._create_object(node)

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

    def _create_object(self, node: Node):

        name = f"N{node.id}"

        obj = bpy.data.objects.new(name, None)
        obj.empty_display_type = 'PLAIN_AXES'
        obj.empty_display_size = 0.1
        obj.location = node.xyz

        bpy.context.scene.collection.objects.link(obj)

        obj.node_rna.node_id = node.id
        obj.node_rna.label = name

        self._nodes[node.id] = obj.name

        return BlNodeWrap(obj)

    def create(self, *, location):

        node = self.domain.create(xyz=location)

        if node.id in self._nodes:
            return self.get(node.id)

        try:
            return self._create_object(node)
        except Exception:
            self.domain.delete(node.id)
            raise

    # ---------- mutation ----------

    def set_location(self, node_id: str, location):

        self.domain.set_location(node_id=node_id, location=location)

        obj = bpy.data.objects[self._nodes[node_id]]
        obj.location = location

    # ---------- deletion ----------

    def delete(self, node_id: str):

        self.domain.delete(node_id)

        name = self._nodes.pop(node_id)
        obj = bpy.data.objects.get(name)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)

    # ---------- replicate ----------

    def replicate(self, node_id: str, offset, count: int):

        original = self.domain[node_id]
        results = []

        for i in range(count):

            new_xyz = (
                original.xyz[0] + offset[0] * (i + 1),
                original.xyz[1] + offset[1] * (i + 1),
                original.xyz[2] + offset[2] * (i + 1),
            )

            node = self.domain.create(xyz=new_xyz)

            if node.id in self._nodes:
                results.append(self.get(node.id))
            else:
                results.append(self._create_object(node))

        return results