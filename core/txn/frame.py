from mathutils import Vector
from blender_adapter.core.object import BlNodeWrap
from blender_adapter.core.object import BlFrameWrap
from blender_adapter.core.runtime import BlRuntime

class BlFrameTxn:
    """
    Transaction scripts for Frames.
    Domain-first, Blender-second.
    """

    def __init__(self, *, runtime : BlRuntime):
        self.st = runtime.structural
        self.bl = runtime.blender

    # -------------------------------------------------
    # CLEAR
    # -------------------------------------------------

    def clear(self):
        """
        Clear the entire system.

        Domain truth is reset.
        Blender representation is cleaned up.
        """

        # 1. BLENDER (cleanup)
        # Remove visual side effects first.
        self.bl.frame.clear()

        # 2. DOMAIN (authoritative reset)
        self.st.frame.clear()

    # -------------------------------------------------
    # CREATE
    # -------------------------------------------------

    def create(self, *, n1_id: str, n2_id: str) -> BlFrameWrap:
        """
        Create a frame between two nodes.
        """

        # 1. DOMAIN (authoritative)
        frame = self.st.frame.create(
            self.st.node,
            n1_id=n1_id,
            n2_id=n2_id,
        )

        frame_id = frame.id

        # 2. BLENDER (idempotent)
        bl_frame = self.bl.frame.get(frame_id)
        if bl_frame is None:
            bl_n1 = self.bl.node.get(n1_id)
            bl_n2 = self.bl.node.get(n2_id)

            bl_frame = self.bl.frame.create(
                frame_id=frame_id,
                name=f"F{frame_id}",
                start=bl_n1.location,
                end=bl_n2.location,
                start_node_id=n1_id,
                end_node_id=n2_id,
            )

        return bl_frame
    
    # -------------------------------------------------
    # MOVE
    # -------------------------------------------------

    def move(self, *,frame_id, direction):
        """
        Interactive nudge / keyboard move.
        """
        # ---------- 1. DOMAIN ----------
        frame = self.st.frame.move(
            node_obj=self.st.node,
            frame_id=frame_id,
            direction=direction,
        )

        # ---------- 2. BLENDER ----------
        bl_frame = self.bl.frame.get(frame_id)
        if bl_frame:
            self.bl.frame.move(
                frame=bl_frame,
                start_node_id=frame.n1_id,
                end_node_id=frame.n2_id,
                direction=direction
            )

    # -------------------------------------------------
    # SET LOCATION (drag commit)
    # -------------------------------------------------

    def set_location(self, *, nodes, frames, frame_id, location):
        """
        Interactive nudge / keyboard move.
        """
        # ---------- 1. DOMAIN ----------
        frame = self.st.frame.set_location(
            nodes=nodes,
            frames=frames,
            frame_id=frame_id,
            location=location,
        )

        # ---------- 2. BLENDER ----------
        bl_frame = self.bl.frame.get(frame_id)
        if bl_frame:
            self.bl.frame.set_location(
                frame=bl_frame,
                start_node_id=frame.n1_id,
                end_node_id=frame.n2_id,
                location=location
            )

    # -------------------------------------------------
    # DELETE
    # -------------------------------------------------

    def delete(self, *, frame_id: str):
        # 1. DOMAIN
        self.st.frame.delete(
        self.st.node,
            frame_id,
        )

        # 2. BLENDER
        bl_frame = self.bl.frame.get(frame_id)
        self.bl.frame.delete(bl_frame)

    # -------------------------------------------------
    # REPLICATE
    # -------------------------------------------------

    def replicate_by_vector(
        self,
        *,
        src_frame_ids: list[str],
        delta: Vector,
        count: int,
    ) -> list[BlFrameWrap]:

        delta_tuple = (delta.x, delta.y, delta.z)

        # ---------- 1. DOMAIN ----------
        frame_batches, node_batches = self.st.frame.replicate(
            nodes=self.st.node,
            frames=self.st.frame,
            src_frame_ids=src_frame_ids,
            delta=delta_tuple,
            count=count,
        )

        # ---------- 2. BLENDER ----------
        src_node_ids = list(set())
        created: list[BlNodeWrap] = []
        seen = set()

        for fid in src_frame_ids:
            bl_frame = self.bl.frame.get(fid)
            for bl_nid in (bl_frame.start_node_id, bl_frame.end_node_id):
                if bl_nid not in seen:
                    seen.add(bl_nid)
                    src_node_ids.append(bl_nid)

        src_bl_nodes = {
            nid: self.bl.node.get(nid)
            for nid in src_node_ids
        }

        for nid, bl_node in src_bl_nodes.items():
            if bl_node is None:
                raise RuntimeError(f"Missing Blender node for {nid}")

        for node_batch in node_batches:
            for src_id, node in zip(src_node_ids, node_batch):
                src_bl = src_bl_nodes[src_id]

                bl_node = self.bl.node.get(node.id)
                if bl_node is None:
                    bl_node = self.bl.node.replicate_from(
                        src=src_bl,
                        node_id=node.id,
                        name=f"N{node.id}",
                        location=node.xyz,
                    )

                created.append(bl_node)

        frame_created: list[BlFrameWrap] = []

        src_bl_frames = {
            fid: self.bl.frame.get(fid)
            for fid in src_frame_ids
        }

        for fid, bl_frame in src_bl_frames.items():
            if bl_frame is None:
                raise RuntimeError(f"Missing Blender frame for {fid}")

        for frame_batch in frame_batches:
            for src_id, frame in zip(src_frame_ids, frame_batch):
                src_bl = src_bl_frames[src_id]

                bl_frame = self.bl.frame.get(frame.id)
                n1 = self.st.node.get(frame.n1_id)
                n2 = self.st.node.get(frame.n2_id)
                if bl_frame is None:
                    bl_frame = self.bl.frame.replicate_from(
                        src=src_bl,
                        frame_id=frame.id,
                        name=f"F{frame.id}",
                        start=n1.xyz,
                        end=n2.xyz,
                        start_node_id=frame.n1_id,
                        end_node_id=frame.n2_id,
                    )

                frame_created.append(bl_frame)

        return frame_created
