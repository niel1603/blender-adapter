import bpy
from mathutils import Vector

class BlNodeProps(bpy.types.PropertyGroup):
    '''
    Blender node properties
    '''
    node_id: bpy.props.StringProperty(name="Node ID") # type: ignore
    label: bpy.props.StringProperty(name="Label") # type: ignore
    
class BlNodeWrap:
    '''
    Blender node wrapper
    '''
    def __init__(self, obj: bpy.types.Object):
        if not hasattr(obj, "node_rna"):
            raise TypeError("Object is not a Node")
        self.obj = obj

    # --- identity ---
    @property
    def id(self) -> str:
        return self.obj.node_rna.node_id

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

class BlFrameWrap:
    def __init__(self, obj: bpy.types.Object):
        if not hasattr(obj, "frame_rna"):
            raise TypeError("Object is not a Frame")
        self.obj = obj

    # --- identity ---
    @property
    def id(self) -> str:
        return self.obj.frame_rna.frame_id

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

    def _get_world_vertex(self, vert_index: int) -> Vector:
        """Return vertex location in world space"""
        v = self.mesh.vertices[vert_index].co
        return self.obj.matrix_world @ v

    def _set_world_vertex(self, vert_index: int, world_location: Vector):
        """Set vertex location using world space input"""
        self.mesh.vertices[vert_index].co = (
            self.obj.matrix_world.inverted() @ world_location
        )

    @property
    def start_node_location(self) -> Vector:
        return self._get_world_vertex(0)

    @start_node_location.setter
    def start_node_location(self, value: Vector):
        self._set_world_vertex(0, value)

    @property
    def end_node_location(self) -> Vector:
        return self._get_world_vertex(1)

    @end_node_location.setter
    def end_node_location(self, value: Vector):
        self._set_world_vertex(1, value)

    # --- transform ---
    @property
    def location(self):
        return self.obj.location

    @location.setter
    def location(self, value):
        self.obj.location = value

    # --- selection ---
    def select(self, context):
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.select_all(action='DESELECT')
        self.obj.select_set(True)
        context.view_layer.objects.active = self.obj

class BlFrameProps(bpy.types.PropertyGroup):
    frame_id: bpy.props.StringProperty(name="Frame ID") # type: ignore
    start_node: bpy.props.StringProperty(name="Start Node ID") # type: ignore
    end_node: bpy.props.StringProperty(name="End Node ID") # type: ignore
    label: bpy.props.StringProperty(name="Label") # type: ignore