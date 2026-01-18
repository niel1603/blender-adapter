from mathutils import Vector
from blender_adapter.core.blender_object.frame import BlFrameObject, BlFrameAdapter
from blender_adapter.core.state._state import BlRuntimeState

class BlFrameTxn:
    """
    Transaction scripts for Frames.
    Domain-first, Blender-second.
    """

    def __init__(self, *, state, adapter):
        self.state: BlRuntimeState = state
        self.adapter: BlFrameAdapter = adapter

    # -------------------------------------------------
    # CREATE
    # -------------------------------------------------

    def create(self, *, n1_id: str, n2_id: str) -> BlFrameObject:
        """
        Create a frame between two nodes.
        """

        # 1. DOMAIN (authoritative)
        frame = self.state.model.frames.create(
            self.state.model.nodes,
            n1_id=n1_id,
            n2_id=n2_id,
        )

        frame_id = frame.id

        # 2. BLENDER (idempotent)
        bl_frame = self.state.frames.get_frame(frame_id)
        if bl_frame is None:
            bl_n1 = self.state.nodes.require_node(n1_id)
            bl_n2 = self.state.nodes.require_node(n2_id)

            bl_frame = self.adapter.create(
                frame_id=frame_id,
                name=f"F{frame_id}",
                start=bl_n1.location,
                end=bl_n2.location,
                start_node_id=n1_id,
                end_node_id=n2_id,
            )

            # 3. INDEX
            self.state.frames.register_frame(frame_id, bl_frame)

        return bl_frame

    # -------------------------------------------------
    # DELETE
    # -------------------------------------------------

    def delete(self, *, frame_id: str):
        # 1. DOMAIN
        self.state.model.frames.delete(
            self.state.model.nodes,
            frame_id,
        )

        # 2. BLENDER
        bl_frame = self.state.frames.require_frame(frame_id)
        self.adapter.delete(bl_frame)

        # 3. INDEX
        self.state.frames.unregister_frame(frame_id)

    # -------------------------------------------------
    # MOVE (rare, but supported)
    # -------------------------------------------------

    def move(self, *, frame_id: str, direction):
        bl_frame = self.state.frames.require_frame(frame_id)
        self.adapter.move(bl_frame, direction)

    # -------------------------------------------------
    # REBUILD GEOMETRY (after node move / undo)
    # -------------------------------------------------

    def rebuild_geometry(self, *, frame_id: str):
        """
        Re-sync frame mesh to node positions.
        """
        frame = self.state.model.frames.get(frame_id)
        bl_frame = self.state.frames.require_frame(frame_id)

        n1 = self.state.nodes.require_node(frame.n1_id)
        n2 = self.state.nodes.require_node(frame.n2_id)

        mesh = bl_frame.mesh
        mesh.clear_geometry()
        mesh.from_pydata(
            [n1.location, n2.location],
            [(0, 1)],
            [],
        )
        mesh.update()

        BlFrameAdapter._center_geometry(bl_frame.obj)

    # -------------------------------------------------
    # REPLICATE (optional / future)
    # -------------------------------------------------

    def replicate_by_vector(
        self,
        *,
        src_frame_ids: list[str],
        delta,
    ) -> list[BlFrameObject]:

        created: list[BlFrameObject] = []

        for src_id in src_frame_ids:
            src_frame = self.state.model.frames.get(src_id)

            # DOMAIN
            frame = self.state.model.frames.create(
                self.state.model.nodes,
                n1_id=src_frame.n1_id,
                n2_id=src_frame.n2_id,
            )

            frame_id = frame.id

            # BLENDER
            src_bl = self.state.frames.require_frame(src_id)

            bl_frame = self.adapter.create(
                frame_id=frame_id,
                name=f"F{frame_id}",
                start=src_bl.mesh.vertices[0].co + Vector(delta),
                end=src_bl.mesh.vertices[1].co + Vector(delta),
                start_node_id=frame.n1_id,
                end_node_id=frame.n2_id,
            )

            self.state.frames.register_frame(frame_id, bl_frame)
            created.append(bl_frame)

        return created
