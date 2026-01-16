# blender_adapter/core/frame_rna.py

import bpy
from blender_adapter.core.base import DomainKind

class BlenderFrame:
    TYPE = DomainKind.FRAME

    def __init__(self, obj: bpy.types.Object):
        if (
            not hasattr(obj, "frame_rna")
            or obj.frame_rna.frame_type != BlenderFrame.TYPE
        ):
            raise TypeError("Object is not a Frame")

        self.obj = obj

    # --- identity ---

    @property
    def id(self) -> str:
        return self.obj.frame_rna.frame_id

    @property
    def type(self) -> str:
        return self.obj.frame_rna.frame_type

    # --- topology ---

    @property
    def start_node_id(self) -> str:
        return self.obj.frame_rna.start_node

    @property
    def end_node_id(self) -> str:
        return self.obj.frame_rna.end_node

    # --- geometry ---

    @property
    def mesh(self) -> bpy.types.Mesh:
        return self.obj.data

    # --- selection ---

    def select(self, context):
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.select_all(action='DESELECT')
        self.obj.select_set(True)
        context.view_layer.objects.active = self.obj

class FrameRNA(bpy.types.PropertyGroup):
    frame_id: bpy.props.StringProperty(name="Frame ID") # type: ignore
    frame_type: bpy.props.StringProperty(name="Frame Type") # type: ignore
    start_node: bpy.props.StringProperty(name="Start Node ID") # type: ignore
    end_node: bpy.props.StringProperty(name="End Node ID") # type: ignore
    label: bpy.props.StringProperty(name="Label") # type: ignore