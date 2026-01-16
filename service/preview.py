import bpy
from mathutils import Vector

class ObjectPreviewService:
    """
    Blender-only preview manager.
    One instance per operator invocation.
    """

    def __init__(self):
        self._active = False

    def begin(self):
        self._active = True

    def update(self):
        raise NotImplementedError

    def restore(self):
        raise NotImplementedError

    def finish(self):
        self.restore()
        self._active = False

class TransformPreview(ObjectPreviewService):
    def __init__(self, objects: list[bpy.types.Object]):
        super().__init__()
        self._objects = objects
        self._original_locations: dict[bpy.types.Object, Vector] = {}

    def begin(self):
        super().begin()
        self._original_locations = {
            obj: obj.location.copy()
            for obj in self._objects
            if obj.name in bpy.data.objects
        }

    def update(self, delta: Vector):
        if not self._active:
            return

        # Restore first
        for obj, loc in self._original_locations.items():
            if obj.name in bpy.data.objects:
                obj.location = loc

        # Apply preview
        for obj in self._original_locations:
            obj.location += delta

    def restore(self):
        for obj, loc in self._original_locations.items():
            if obj.name in bpy.data.objects:
                obj.location = loc

class ClonePreview(ObjectPreviewService):
    def __init__(self, context, objects: list[bpy.types.Object]):
        super().__init__()
        self._context = context
        self._objects = objects
        self._clones: list[bpy.types.Object] = []

    def update(self, offsets: list[Vector]):
        self.restore()

        for obj in self._objects:
            if obj.get("_som_preview"):
                continue

            for offset in offsets:
                clone = obj.copy()
                if obj.data:
                    clone.data = obj.data.copy()

                clone.location = obj.location + offset
                clone["_som_preview"] = True

                self._context.collection.objects.link(clone)
                clone.select_set(False)

                self._clones.append(clone)

    def restore(self):
        for obj in self._clones:
            if obj.name in bpy.data.objects:
                bpy.data.objects.remove(obj, do_unlink=True)
        self._clones.clear()
