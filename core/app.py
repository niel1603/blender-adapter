import bpy
from blender_adapter.core.runtime import BlRuntime
from blender_adapter.core.txn._txn import BlModelTxn

class BlLiveSession:
    """
    Scene-scoped runtime container.
    Owns runtime state and operations API.
    """

    def __init__(self, scene: bpy.types.Scene):
        self.scene = scene

        # --- sync model (Blender <-> Structural) ---
        self.runtime = BlRuntime(scene)

        # --- operations API ---
        self.ops = BlModelTxn(runtime=self.runtime)

        self._alive = True

    # -------------------------------------------------
    # lifecycle hooks
    # -------------------------------------------------

    def rebuild_from_scene(self):
        """Re-sync after undo / redo / file load."""
        if not self._alive:
            return
        self.runtime.rebuild()

    def dispose(self):
        """Explicit teardown."""
        if not self._alive:
            return

        self._alive = False


class BlApplication:
    """
    Addon-level application root.
    Process-scoped.
    Owns all live scene sessions.
    """

    def __init__(self):
        self._sessions: dict[int, BlLiveSession] = {}
        self._running = False

    # -------------------------------------------------
    # application lifecycle
    # -------------------------------------------------

    def start(self):
        if self._running:
            return
        self._running = True

        # register handlers here if needed
        # bpy.app.handlers.load_post.append(self._on_load)

    def stop(self):
        if not self._running:
            return

        for session in self._sessions.values():
            session.dispose()

        self._sessions.clear()
        self._running = False

        # unregister handlers here

    # -------------------------------------------------
    # scene session API (SapModel analogue)
    # -------------------------------------------------

    def session(self, scene: bpy.types.Scene) -> BlLiveSession:
        """
        Get or create a live session for a scene.
        """
        key = scene.as_pointer()

        session = self._sessions.get(key)
        if session is None:
            session = BlLiveSession(scene)
            self._sessions[key] = session

        return session

    def has_session(self, scene: bpy.types.Scene) -> bool:
        return scene.as_pointer() in self._sessions

    def drop_session(self, scene: bpy.types.Scene):
        key = scene.as_pointer()
        session = self._sessions.pop(key, None)
        if session:
            session.dispose()

_app: BlApplication | None = None


def bl_app() -> BlApplication:
    global _app
    if _app is None:
        _app = BlApplication()
    return _app
