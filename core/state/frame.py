import bpy
from blender_adapter.core.blender_object.frame import BlFrameObject

class BlFrameIndex:
    """
    Scene-scoped identity index for Frames.

    Maps frame_id -> Blender object name.
    Owns no Blender data and performs no mutations.
    Rebuildable after undo / reload.
    """

    def __init__(self):
        self._frames: dict[str, str] = {}  # frame_id -> object name

    # ---------- rebuild (undo / reload safe) ----------

    def rebuild(self, scene: bpy.types.Scene):
        self._frames.clear()

        for obj in scene.objects:
            if not hasattr(obj, "frame_rna"):
                continue

            # optional but recommended validation
            # if obj.frame_rna.frame_type != BlFrameObject.TYPE:
            #     continue

            frame_id = obj.frame_rna.frame_id
            if not frame_id:
                continue

            # detect duplicate IDs early (important!)
            if frame_id in self._frames:
                raise RuntimeError(
                    f"Duplicate frame_id '{frame_id}' on objects "
                    f"'{self._frames[frame_id]}' and '{obj.name}'"
                )

            self._frames[frame_id] = obj.name

    # ---------- access ----------

    def get_frame(self, frame_id: str) -> BlFrameObject | None:
        name = self._frames.get(frame_id)
        if not name:
            return None

        obj = bpy.data.objects.get(name)
        if not obj or not hasattr(obj, "frame_rna"):
            return None

        try:
            return BlFrameObject(obj)
        except TypeError:
            return None

    def require_frame(self, frame_id: str) -> BlFrameObject:
        frame = self.get_frame(frame_id)
        if not frame:
            raise KeyError(f"Blender Frame not found for id '{frame_id}'")
        return frame

    def has_frame(self, frame_id: str) -> bool:
        return frame_id in self._frames

    def iter_frames(self) -> list[BlFrameObject]:
        result: list[BlFrameObject] = []

        for frame_id in list(self._frames.keys()):
            frame = self.get_frame(frame_id)
            if frame:
                result.append(frame)

        return result

    # ---------- reverse lookup ----------

    def get_frame_id_by_object(
        self,
        obj: bpy.types.Object,
    ) -> str | None:
        """
        Resolve frame_id from a Blender object.
        Returns None if object is not a registered Frame.
        Undo / rebuild safe.
        """
        if not hasattr(obj, "frame_rna"):
            return None

        if obj.frame_rna.frame_type != BlFrameObject.TYPE:
            return None

        frame_id = obj.frame_rna.frame_id
        if not frame_id:
            return None

        # validate against index
        if frame_id not in self._frames:
            return None

        return frame_id

    # ---------- registration (fast path) ----------

    def register_frame(self, frame_id: str, frame: BlFrameObject):
        self._frames[frame_id] = frame.obj.name

    def unregister_frame(self, frame_id: str):
        self._frames.pop(frame_id, None)
