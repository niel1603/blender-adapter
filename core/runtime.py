import bpy

from structural_om.core.model import StructuralModel
from blender_adapter.core.model import BlenderModel

class BlRuntime:
    """
    Runtime bridge between BlenderModel and StructuralModel.
    """

    def __init__(self, scene: bpy.types.Scene):
        self.scene = scene
        self.structural = StructuralModel()
        self.blender = BlenderModel(scene)
        self.rebuild()

    # ----------------------------
    # REBUILD
    # ----------------------------

    def rebuild(self):
        """
        Transactional rebuild.

        Blender state → identity indices → domain model
        Undo / redo / load safe.
        """

        # ------------------------------------
        # PHASE 1: Discover Blender state
        # ------------------------------------

        self.blender.rebuild()

        # ------------------------------------
        # PHASE 2: Reset domain model
        # ------------------------------------

        self.structural.clear()

        # ------------------------------------
        # PHASE 3: Materialize nodes
        # ------------------------------------

        for bl_node in self.blender.node:
            self.structural.node.create(
                xyz=tuple(bl_node.location),
                node_id=bl_node.id,
            )

        # ------------------------------------
        # PHASE 4: Materialize frames
        # ------------------------------------

        for bl_frame in self.blender.frame:
            self.structural.frame.create(
                nodes=self.structural.node,
                frame_id=bl_frame.id,
                n1_id=bl_frame.start_node_id,
                n2_id=bl_frame.end_node_id,
            )

        # ------------------------------------
        # PHASE 5: Seal rebuild (ID pools)
        # ------------------------------------

        self.structural.node.ids.rebuild_from_existing(
            self.structural.node.nodes.keys()
        )
        self.structural.frame.ids.rebuild_from_existing(
            self.structural.frame.frames.keys()
        )
