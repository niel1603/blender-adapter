import bpy
from mathutils import Vector

class BlFrameObject:
    def __init__(self, obj: bpy.types.Object):
        if (not hasattr(obj, "frame_rna")):
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

    # --- selection ---

    def select(self, context):
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.select_all(action='DESELECT')
        self.obj.select_set(True)
        context.view_layer.objects.active = self.obj

class FrameRNA(bpy.types.PropertyGroup):
    frame_id: bpy.props.StringProperty(name="Frame ID") # type: ignore
    start_node: bpy.props.StringProperty(name="Start Node ID") # type: ignore
    end_node: bpy.props.StringProperty(name="End Node ID") # type: ignore
    label: bpy.props.StringProperty(name="Label") # type: ignore

class BlFrameAdapter:

    # ---------- ID ----------
    @staticmethod
    def next_id(prefix="F"):
        max_index = 0
        for obj in bpy.data.objects:
            if obj.name.startswith(prefix):
                suffix = obj.name[len(prefix):]
                if suffix.isdigit():
                    max_index = max(max_index, int(suffix))
        idx = max_index + 1
        return str(idx), f"{prefix}{idx}"

    # ---------- CREATE ----------

    @staticmethod
    def create(
        *,
        frame_id: str,
        name: str,
        start,
        end,
        start_node_id: str,
        end_node_id: str,
        collection=None,
    ) -> BlFrameObject:

        if collection is None:
            collection = bpy.context.scene.collection

        mesh = bpy.data.meshes.new(f"{name}_Mesh")
        mesh.from_pydata([start, end], [(0, 1)], [])
        mesh.update()

        obj = bpy.data.objects.new(name, mesh)
        collection.objects.link(obj)

        BlFrameAdapter._center_geometry(obj)

        rna = obj.frame_rna
        rna.frame_id = frame_id
        rna.start_node = start_node_id
        rna.end_node = end_node_id
        rna.label = name

        return BlFrameObject(obj)

    # ---------- GEOMETRY ----------
    @staticmethod
    def _center_geometry(obj):
        mesh = obj.data
        if not mesh.vertices:
            return

        center = Vector()
        for v in mesh.vertices:
            center += v.co
        center /= len(mesh.vertices)

        for v in mesh.vertices:
            v.co -= center

        obj.location += obj.matrix_world.to_3x3() @ center

    # ---------- MOVE ----------
    @staticmethod
    def move(frame: BlFrameObject, direction):
        frame.obj.location += Vector(direction)

    # ---------- DELETE ----------
    @staticmethod
    def delete(frame: BlFrameObject):
        bpy.data.objects.remove(frame.obj, do_unlink=True)

    # ---------- REPLICATE ----------
    @staticmethod
    def replicate(
        frame: BlFrameObject,
        *,
        direction=(0, 0, 0),
        collection=None,
    ) -> BlFrameObject:

        src = frame.obj

        if collection is None:
            collection = src.users_collection[0]

        frame_id, name = BlFrameAdapter.next_id("F")

        new_obj = src.copy()
        new_obj.data = src.data.copy()
        new_obj.name = name
        new_obj.location = src.location + Vector(direction)

        collection.objects.link(new_obj)

        rna = new_obj.frame_rna
        rna.frame_id = frame_id
        rna.start_node = src.frame_rna.start_node
        rna.end_node = src.frame_rna.end_node
        rna.label = name

        return BlFrameObject(new_obj)
    
    # ---------- READ (single) ----------

    @staticmethod
    def get_by_id(frame_id: str) -> BlFrameObject | None:
        for obj in bpy.data.objects:
            if (
                hasattr(obj, "frame_rna")
                and obj.frame_rna.frame_id == frame_id
            ):
                return BlFrameObject(obj)
        return None

    @staticmethod
    def get_by_object(obj: bpy.types.Object) -> BlFrameObject | None:
        try:
            return BlFrameObject(obj)
        except TypeError:
            return None

    # ---------- READ (collection) ----------

    @staticmethod
    def all() -> list[BlFrameObject]:
        result: list[BlFrameObject] = []

        for obj in bpy.data.objects:
            if (
                hasattr(obj, "frame_rna")
            ):
                result.append(BlFrameObject(obj))

        return result

    @staticmethod
    def selected(context) -> list[BlFrameObject]:
        result: list[BlFrameObject] = []

        for obj in context.selected_objects:
            if (
                hasattr(obj, "frame_rna")
            ):
                result.append(BlFrameObject(obj))

        return result