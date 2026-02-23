import bpy

from structural_om.core.model import StructuralModel

from blender_adapter.core.api.node import BlNodeObj
from blender_adapter.core.api.frame import BlFrameObj

class BlenderModel:
    """
    Blender-side infrastructure layer.
    Mirrors domain state.
    """

    def __init__(self, *, scene: bpy.types.Scene, structural: StructuralModel):
        self.scene = scene
        self.structural = structural

        self.node = BlNodeObj(structural.node)
        self.frame = BlFrameObj()
