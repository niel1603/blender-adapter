import bpy

from structural_om.domain.model import StructuralModel
from blender_adapter.core.state.node import BlNodeIndex
from blender_adapter.core.state.frame import BlFrameIndex

class BlRuntimeState:
    def __init__(self, scene: bpy.types.Scene):
        self.scene = scene
        self.model = StructuralModel()

        self.nodes = BlNodeIndex()
        self.frames = BlFrameIndex()

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

        self.nodes.rebuild(self.scene)
        self.frames.rebuild(self.scene)

        # ------------------------------------
        # PHASE 2: Reset domain model
        # ------------------------------------

        self.model.clear()

        # ------------------------------------
        # PHASE 3: Materialize nodes (authoritative)
        # ------------------------------------

        for bl_node in self.nodes.iter_nodes():
            self.model.nodes.create(
                xyz=tuple(bl_node.location),
                node_id=bl_node.id,
            )

        # ------------------------------------
        # PHASE 4: Materialize frames
        # ------------------------------------

        for bl_frame in self.frames.iter_frames():
            self.model.frames.create(
                nodes=self.model.nodes,
                frame_id=bl_frame.id,
                n1_id=bl_frame.start_node_id,
                n2_id=bl_frame.end_node_id,
            )

        # ------------------------------------
        # PHASE 5: Seal rebuild (ID pools)
        # ------------------------------------

        self.model.nodes.ids.rebuild_from_existing(
            self.model.nodes.all().keys()
        )
        self.model.frames.ids.rebuild_from_existing(
            self.model.frames.all().keys()
        )