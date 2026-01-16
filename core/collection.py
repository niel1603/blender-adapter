import bpy
from blender_adapter.core.object.node import BlenderNode

class BlenderObjectCollection:

    """
    Scene-scoped identity index.

    Maps domain IDs <-> Blender objects.
    Owns no Blender data and performs no mutations.
    Rebuildable after undo / file reload.
    """

    def __init__(self):
        self._nodes: dict[str, str] = {}   # node_id -> object name

    # ---------- rebuild (undo / reload safe) ----------

    def rebuild(self, scene: bpy.types.Scene):
        self._nodes.clear()

        for obj in scene.objects:
            if not hasattr(obj, "node_rna"):
                continue

            node_id = obj.node_rna.node_id
            if node_id:
                self._nodes[node_id] = obj.name

    # ---------- access ----------

    def get_node(self, node_id: str) -> BlenderNode | None:
        name = self._nodes.get(node_id)
        if not name:
            return None

        obj = bpy.data.objects.get(name)
        if not obj or not hasattr(obj, "node_rna"):
            return None

        try:
            return BlenderNode(obj)
        except TypeError:
            return None

    def require_node(self, node_id: str) -> BlenderNode:
        node = self.get_node(node_id)
        if not node:
            raise KeyError(f"BlenderNode not found for id '{node_id}'")
        return node

    def has_node(self, node_id: str) -> bool:
        return node_id in self._nodes

    def iter_nodes(self) -> list[BlenderNode]:
        result: list[BlenderNode] = []

        for node_id in list(self._nodes.keys()):
            node = self.get_node(node_id)
            if node:
                result.append(node)

        return result
    

    # ---------- reverse lookup ----------

    def get_node_id_by_object(
        self,
        obj: bpy.types.Object,
    ) -> str | None:
        """
        Resolve node_id from a Blender object.
        Returns None if object is not a registered Node.
        Undo / rebuild safe.
        """
        if not hasattr(obj, "node_rna"):
            return None

        node_id = obj.node_rna.node_id
        if not node_id:
            return None

        # validate against index (important!)
        if node_id not in self._nodes:
            return None

        return node_id

    # ---------- registration (fast path) ----------

    def register_node(self, node_id: str, node: BlenderNode):
        self._nodes[node_id] = node.obj.name

    def unregister_node(self, node_id: str):
        self._nodes.pop(node_id, None)