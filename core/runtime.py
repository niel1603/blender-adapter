import bpy

from structural_om.core.model import StructuralModel
from blender_adapter.core.model import BlenderModel

class BlRuntime:
    """
    Runtime bridge between StructuralModel (authoritative)
    and BlenderModel (mirror).
    """

    def __init__(self, scene: bpy.types.Scene):
        self.scene = scene

        # 1. DOMAIN FIRST
        self.structural = StructuralModel()

        # 2, BLENDER REFERENCES DOMAIN
        self.blender = BlenderModel(
            scene=scene,
            structural=self.structural,
        )

    # ----------------------------
    # REBUILD
    # ----------------------------

    def rebuild_from_scene(self):

        # 1. Extract raw data
        print("[SOM] Rebuild Phase 1: Extracting Blender state")
        nodes = self.blender.node.extract_from_scene(self.scene)

        # 2. Rebuild domain
        print("[SOM] Rebuild Phase 2: Rebuilding domain")
        self.structural.node.rebuild(nodes)

        # 3. Rebuild blender identity index
        print("[SOM] Rebuild Phase 3: Rebuilding blender identity")
        self.blender.node.rebuild_identity_from_scene(self.scene)

        # 4. Sync differences
        print("[SOM] Rebuild Phase 4: Syncing Blender mirror")
        self.blender.node.sync_from_domain()
