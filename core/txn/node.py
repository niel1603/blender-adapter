from mathutils import Vector
from blender_adapter.core.object import BlNodeWrap
from blender_adapter.core.runtime import BlRuntime

class BlNodeTxn:

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
        self.bl.node.clear()

        # 2. DOMAIN (authoritative reset)
        self.st.node.clear()

    # -------------------------------------------------
    # CREATE
    # -------------------------------------------------

    def create(self, *, location) -> BlNodeWrap:
        """
        Create or reuse a node at the given location.

        Domain decides identity.
        Blender reflects domain state.
        """

        # 1. DOMAIN (authoritative)
        node = self.st.node.create(xyz=tuple(location))
        node_id = node.id

        # 2. BLENDER (idempotent)
        bl_node = self.bl.node.get(node_id)
        if bl_node is None:
            bl_node = self.bl.node.create(
                node_id=node_id,
                name=f"N{node_id}",
                location=node.xyz,
            )

        return bl_node

    # -------------------------------------------------
    # MOVE
    # -------------------------------------------------

    def move(self, *, node_id, direction):
        """
        Interactive nudge / keyboard move.
        """

        # ---------- 1. DOMAIN ----------
        self.st.node.move(
            node_id=node_id, 
            direction=direction)

        # ---------- 2. BLENDER ----------
        bl_node = self.bl.node.get(node_id)
        if bl_node:
            self.bl.node.move(bl_node, direction)

    # -------------------------------------------------
    # SET LOCATION (drag commit)
    # -------------------------------------------------

    def set_location(self, *, node_id, location):
        """
        Drag commit: absolute placement.
        """

        # ---------- 1. DOMAIN ----------
        self.st.node.set_location(node_id=node_id, location=location)

        # ---------- 2. BLENDER ----------
        bl_node = self.bl.node.get(node_id)
        if bl_node:
            self.bl.node.set_location(bl_node, location)

    # -------------------------------------------------
    # DELETE
    # -------------------------------------------------

    def delete(self, *, node_id):
        
        # 1. DOMAIN
        self.st.node.delete(node_id=node_id)

        # 2. BLENDER
        bl_node = self.bl.node.get(node_id)
        self.bl.node.delete(bl_node)

    # -------------------------------------------------
    # REPLICATE
    # -------------------------------------------------
            
    def replicate_by_vector(
        self,
        *,
        src_node_ids: list[str],
        delta: Vector,
        count: int,
    ) -> list[BlNodeWrap]:

        delta_tuple = (delta.x, delta.y, delta.z)

        # ---------- 1. DOMAIN ----------
        batches = self.st.node.replicate(
            src_node_ids=src_node_ids,
            delta=delta_tuple,
            count=count,
        )

        # ---------- 2. BLENDER ----------
        created: list[BlNodeWrap] = []

        src_bl_nodes = {
            nid: self.bl.node.get(nid)
            for nid in src_node_ids
        }

        for nid, bl_node in src_bl_nodes.items():
            if bl_node is None:
                raise RuntimeError(f"Missing Blender node for {nid}")

        for batch in batches:
            for src_id, node in zip(src_node_ids, batch):
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

        return created

