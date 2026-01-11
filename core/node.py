import bpy
from blender_adapter.core.base import DomainKind

class BlenderNode:
    TYPE = DomainKind.NODE

    def __init__(self, obj: bpy.types.Object):
        if (
            not hasattr(obj, "node_rna")
            or obj.node_rna.node_type != BlenderNode.TYPE
        ):
            raise TypeError("Object is not a Node")

        self.obj = obj

    # --- identity ---
    @property
    def id(self):
        return self.obj.node_rna.node_id

    @property
    def type(self):
        return self.obj.node_rna.node_type

    # --- transform ---
    @property
    def location(self):
        return self.obj.location

    @location.setter
    def location(self, value):
        self.obj.location = value

    # --- selection ---
    def select(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        self.obj.select_set(True)
        context.view_layer.objects.active = self.obj

class NodeRNA(bpy.types.PropertyGroup):
    node_id: bpy.props.StringProperty(name="Node ID") # type: ignore
    node_type: bpy.props.StringProperty(name="Node Type") # type: ignore
    label: bpy.props.StringProperty(name="Label") # type: ignore