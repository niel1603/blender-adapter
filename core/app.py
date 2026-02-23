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

        # --- pure construction (NO rebuild here) ---
        self.runtime = BlRuntime(scene)
        self.ops = BlModelTxn(runtime=self.runtime)

        self._alive = True
        self._dirty = True

    # -------------------------------------------------
    # state management
    # -------------------------------------------------

    def mark_dirty(self):
        if not self._alive:
            return
        self._dirty = True

    def ensure_ready(self):
        """
        Perform lazy rebuild if needed.
        Safe to call before any operation.
        """
        if not self._alive:
            return

        if self._dirty:
            print("\n[SOM] >>> Rebuild triggered")
            self.runtime.rebuild_from_scene()
            self._dirty = False
            print("[SOM] <<< Rebuild completed\n")

    # -------------------------------------------------
    # lifecycle
    # -------------------------------------------------

    def dispose(self):
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

        if self._on_load_post not in bpy.app.handlers.load_post:
            bpy.app.handlers.load_post.append(self._on_load_post)

        if self._on_undo_post not in bpy.app.handlers.undo_post:
            bpy.app.handlers.undo_post.append(self._on_undo_post)

    def stop(self):
        if not self._running:
            return

        bpy.app.handlers.load_post.remove(self._on_load_post)
        bpy.app.handlers.undo_post.remove(self._on_undo_post)

        for session in self._sessions.values():
            session.dispose()

        self._sessions.clear()
        self._running = False

    def _on_load_post(self, _):
        for session in self._sessions.values():
            session.mark_dirty()

    def _on_undo_post(self, _):
        for session in self._sessions.values():
            session.mark_dirty()

    # -------------------------------------------------
    # scene session API (SapModel analogue)
    # -------------------------------------------------

    def start_session(self, scene: bpy.types.Scene) -> BlLiveSession:
        key = scene.as_pointer()
        if key in self._sessions:
            return self._sessions[key]

        session = BlLiveSession(scene)
        self._sessions[key] = session
        return session


    def get_session(self, scene: bpy.types.Scene) -> BlLiveSession | None:
        return self._sessions.get(scene.as_pointer())

    # def has_session(self, scene: bpy.types.Scene) -> bool:
    #     return scene.as_pointer() in self._sessions

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
