import bpy
from mathutils import Vector

class BlNodeObject:
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

class NodeRNA(bpy.types.PropertyGroup):
    node_id: bpy.props.StringProperty(name="Node ID") # type: ignore
    label: bpy.props.StringProperty(name="Label") # type: ignore

class BlNodeAdapter:

    @staticmethod
    def create(*, node_id, name, location, size, collection=None) -> BlNodeObject:
        if collection is None:
            collection = bpy.context.scene.collection

        obj = bpy.data.objects.new(name, None)
        obj.empty_display_type = 'PLAIN_AXES'
        obj.empty_display_size = size
        obj.location = location
        collection.objects.link(obj)

        rna = obj.node_rna
        rna.node_id = node_id
        rna.label = name

        return BlNodeObject(obj)

    @staticmethod
    def move(node: BlNodeObject, direction):
        node.obj.location += Vector(direction)

    @staticmethod
    def set_location(node: BlNodeObject, location):
        node.obj.location = location

    @staticmethod
    def delete(node: BlNodeObject):
        bpy.data.objects.remove(node.obj, do_unlink=True)

    @staticmethod
    def replicate_from(
        src: BlNodeObject,
        *,
        node_id: str,
        name: str,
        location=None,
        collection=None,
    ) -> BlNodeObject:

        src_obj = src.obj

        if location is None:
            location = src_obj.location.copy()

        if collection is None:
            collection = src_obj.users_collection[0]

        obj = bpy.data.objects.new(name, None)
        obj.empty_display_type = src_obj.empty_display_type
        obj.empty_display_size = src_obj.empty_display_size
        obj.location = location
        collection.objects.link(obj)

        rna = obj.node_rna
        rna.node_id = node_id
        rna.label = name

        return BlNodeObject(obj)
    
    # ---------- READ (single) ----------

    @staticmethod
    def get_by_id(node_id: str) -> BlNodeObject | None:
        for obj in bpy.data.objects:
            if (
                hasattr(obj, "node_rna")
                and obj.node_rna.node_id == node_id
            ):
                return BlNodeObject(obj)
        return None

    @staticmethod
    def get_by_object(obj: bpy.types.Object) -> BlNodeObject | None:
        try:
            return BlNodeObject(obj)
        except TypeError:
            return None

    # ---------- READ (collection) ----------

    @staticmethod
    def all() -> list[BlNodeObject]:
        result: list[BlNodeObject] = []

        for obj in bpy.data.objects:
            if (
                hasattr(obj, "node_rna")
            ):
                result.append(BlNodeObject(obj))

        return result

    @staticmethod
    def selected(context) -> list[BlNodeObject]:
        result: list[BlNodeObject] = []

        for obj in context.selected_objects:
            if (
                hasattr(obj, "node_rna")
            ):
                result.append(BlNodeObject(obj))

        return result