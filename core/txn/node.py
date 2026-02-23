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
        Clear entire system.
        Domain resets.
        Blender mirrors.
        """

        # 1. DOMAIN
        self.st.node.clear()

        # 2. BLENDER
        self.bl.node.clear()


    # -------------------------------------------------
    # CREATE
    # -------------------------------------------------

    def create(self, *, location) -> BlNodeWrap:

        # 1. CREATE DOMAIN
        node = self.st.node.create(xyz=tuple(location))

        # If already mirrored, reuse
        existing = self.bl.node.get(node.id)
        if existing:
            return existing

        try:
            # 2. CREATE BLENDER
            return self.bl.node._create_object(node)

        except Exception:
            # 3. ROLLBACK DOMAIN
            self.st.node.delete(node.id)
            raise

    # -------------------------------------------------
    # MOVE
    # -------------------------------------------------

    def move(self, *, node_id, direction):

        node = self.st.node[node_id]

        new_xyz = (
            node.xyz[0] + direction[0],
            node.xyz[1] + direction[1],
            node.xyz[2] + direction[2],
        )

        # 1. DOMAIN VALIDATES + MUTATES
        self.st.node.set_location(
            node_id=node_id,
            location=new_xyz,
        )

        try:
            # 2. BLENDER MIRROR
            self.bl.node.set_location(node_id, new_xyz)

        except Exception:
            # 3. ROLLBACK DOMAIN
            self.st.node.set_location(
                node_id=node_id,
                location=node.xyz  # restore previous
            )
            raise

    # -------------------------------------------------
    # SET LOCATION (drag commit)
    # -------------------------------------------------

    def set_location(self, *, node_id, location):

        old_xyz = self.st.node[node_id].xyz

        # 1. DOMAIN VALIDATES + MUTATES
        self.st.node.set_location(
            node_id=node_id,
            location=location,
        )

        try:
            # 2. BLENDER MIRROR
            self.bl.node.set_location(node_id, location)

        except Exception:
            # 3. ROLLBACK DOMAIN
            self.st.node.set_location(
                node_id=node_id,
                location=old_xyz,
            )
            raise


    # -------------------------------------------------
    # DELETE
    # -------------------------------------------------

    def delete(self, *, node_id):

        # 1. DELETE DOMAIN
        # create snapshot for rollback to
        node_snapshot = self.st.node[node_id]

        self.st.node.delete(node_id)

        try:
            # 2. BLENDER MIRROR
            self.bl.node.delete(node_id)

        except Exception:
            # 3. ROLLBACK DOMAIN
            self.st.node.create(
                xyz=node_snapshot.xyz,
                node_id=node_snapshot.id,
            )
            raise

    # -------------------------------------------------
    # REPLICATE
    # -------------------------------------------------
                
    def replicate_by_vector(
        self,
        *,
        src_node_ids: list[str],
        delta,
        count: int,
    ) -> list[BlNodeWrap]:

        delta_tuple = (delta.x, delta.y, delta.z)

        created_nodes = []
        created_bl = []

        try:
            # 1. REPLICATE DOMAIN FIRST
            for i in range(count):
                for src_id in src_node_ids:

                    src_node = self.st.node[src_id]

                    new_xyz = (
                        src_node.xyz[0] + delta_tuple[0] * (i + 1),
                        src_node.xyz[1] + delta_tuple[1] * (i + 1),
                        src_node.xyz[2] + delta_tuple[2] * (i + 1),
                    )

                    node = self.st.node.create(xyz=new_xyz)
                    created_nodes.append(node)

            # 2. BLENDER MIRROR
            for node in created_nodes:

                bl_node = self.bl.node.get(node.id)
                if bl_node is None:
                    bl_node = self.bl.node._create_object(node)

                created_bl.append(bl_node)

            return created_bl

        except Exception:

            # 3. DOMAIN ROLLBACK
            for node in reversed(created_nodes):
                if node.id in self.st.node:
                    self.st.node.delete(node.id)

            raise