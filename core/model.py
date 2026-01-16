import bpy

from structural_om.domain.model import StructuralModel
from blender_adapter.core.collection import BlenderObjectCollection

class BlenderModel:
    """
    Scene-scoped runtime model.
    Rebuilt after undo/redo/load.
    """

    def __init__(self, scene: bpy.types.Scene):
        self.scene = scene
        self.structural = StructuralModel()
        self.objects = BlenderObjectCollection()
        self.rebuild()

    def rebuild(self):
        # 1. discover Blender state
        self.objects.rebuild(self.scene)

        # 2. reset domain model
        self.structural.clear()

        # 3. rebuild nodes (authoritative)
        for bl_node in self.objects.iter_nodes():
            self.structural.add_node_forced(
                node_id=bl_node.id,
                xyz=tuple(bl_node.location),
            )

        # 4. rebuild ID pools properly
        self.structural.node_ids.rebuild_from_existing(
            list(self.structural.nodes.keys())
        )