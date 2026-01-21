import bpy
from blender_adapter.core.api.node import BlNodeObj
from blender_adapter.core.api.frame import BlFrameObj

class BlenderModel:
    """
    Blender-side model.
    Owns all Blender object APIs and indices.
    """

    def __init__(self, scene: bpy.types.Scene):
        self.scene = scene

        self.node = BlNodeObj()
        self.frame = BlFrameObj()

    # ----------------------------
    # REBUILD (Blender discovery)
    # ----------------------------

    def rebuild(self):
        """
        Rebuild Blender identity indices from scene.
        Undo / redo / reload safe.
        """
        self.node.rebuild(self.scene)
        self.frame.rebuild(self.scene)
