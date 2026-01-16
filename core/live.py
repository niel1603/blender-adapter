import bpy
from blender_adapter.core.model import BlenderModel
from blender_adapter.core.controller import BlenderModelController
from blender_adapter.core.adapter.node import BlenderNodeAdapter


class BlenderLiveSession:
    """
    Scene-scoped runtime container.
    Owns BlenderModel and controller.
    """

    def __init__(self, scene: bpy.types.Scene):
        self.scene = scene

        # --- sync model (Blender <-> Structural) ---
        self.model = BlenderModel(scene)

        # --- controller ---
        self.controller = BlenderModelController(
            structural_model=self.model.structural,
            object_collection=self.model.objects,
            node_adapter=BlenderNodeAdapter,
        )

    # -------------------------------------------------
    # lifecycle hooks
    # -------------------------------------------------

    def rebuild_from_scene(self):
        """
        Re-sync after undo / redo / file load.
        """
        self.model.rebuild()

# -------------------------------------------------
# Scene-scoped access helpers
# -------------------------------------------------

# scene_ptr (int) -> BlenderLiveSession
_sessions: dict[int, BlenderLiveSession] = {}

def get_live_session(context) -> BlenderLiveSession:
    scene = context.scene
    key = scene.as_pointer()

    session = _sessions.get(key)
    if session is None:
        session = BlenderLiveSession(scene)
        _sessions[key] = session

    return session

def has_live_session(scene) -> bool:
    return scene.as_pointer() in _sessions

def get_live_session_by_scene(scene) -> BlenderLiveSession | None:
    return _sessions.get(scene.as_pointer())

def drop_live_session(scene):
    _sessions.pop(scene.as_pointer(), None)
