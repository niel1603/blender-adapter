import bpy
from blender_adapter.core.state._state import BlRuntimeState
from blender_adapter.core.ops._ops import BlModelOps

class BlLiveSession:
    """
    Scene-scoped runtime container.
    Owns runtime state and operations API.
    """

    def __init__(self, scene: bpy.types.Scene):
        self.scene = scene

        # --- sync model (Blender <-> Structural) ---
        self.state = BlRuntimeState(scene)

        # --- operations API ---
        self.ops = BlModelOps(state=self.state)

        self._alive = True

    # -------------------------------------------------
    # lifecycle hooks
    # -------------------------------------------------

    def rebuild_from_scene(self):
        """Re-sync after undo / redo / file load."""
        if not self._alive:
            return
        self.state.rebuild()

    def dispose(self):
        """Explicit teardown."""
        if not self._alive:
            return

        self._alive = False
