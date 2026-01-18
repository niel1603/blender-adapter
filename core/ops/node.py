from mathutils import Vector
from blender_adapter.core.blender_object.node import BlNodeObject, BlNodeAdapter
from blender_adapter.core.state._state import BlRuntimeState

class BlNodeTxn:

    def __init__(self, *, state, adapter):
        self.state   : BlRuntimeState = state
        self.adapter : BlNodeAdapter  = adapter

    # -------------------------------------------------
    # CREATE (domain-first, blender-second)
    # -------------------------------------------------

    def create(self, *, location, size):
        """
        Create or reuse a node at the given location.

        Domain decides identity.
        Blender reflects domain state.
        """

        # 1. DOMAIN (authoritative)
        node = self.state.model.nodes.create(xyz=tuple(location))
        node_id = node.id

        # 2. BLENDER (idempotent)
        bl_node = self.state.nodes.get_node(node_id)
        if bl_node is None:
            bl_node = self.adapter.create(
                node_id=node_id,
                name=f"N{node_id}",
                location=node.xyz,
                size=size,
            )
            # 3. INDEX
            self.state.nodes.register_node(node_id, bl_node)

        return bl_node
    
    def get_or_create(self, *, location, size):
        """
        Create or reuse a node at the given location.
        """

        # 1. DOMAIN (authoritative)
        node = self.state.model.nodes.get_or_create(
            xyz=tuple(location)
        )
        node_id = node.id

        # 2. BLENDER (idempotent)
        bl_node = self.state.nodes.get_node(node_id)
        if bl_node is None:
            bl_node = self.adapter.create(
                node_id=node_id,
                name=f"N{node_id}",
                location=node.xyz,
                size=size,
            )
            self.state.nodes.register_node(node_id, bl_node)

        return bl_node

    # ---------- MOVE ----------

    def move(self, *, node_id, direction):
        # 1. DOMAIN 
        node = self.state.model.nodes.get(node_id)

        # 2. BLENDER
        node.xyz = tuple(
            node.xyz[i] + direction[i] for i in range(3)
        )
        bl_node = self.state.nodes.require_node(node_id)
        self.adapter.move(bl_node, direction)

    # ---------- SET LOCATION (drag commit) ----------

    def set_location(self, *, node_id, location):
        # 1. DOMAIN 
        node = self.state.model.nodes.get(node_id)
        node.xyz = location

        # 2. BLENDER
        bl_node = self.state.nodes.require_node(node_id)
        self.adapter.set_location(bl_node, location)

    # ---------- DELETE ----------

    def delete(self, *, node_id):
        
        # 1. DOMAIN
        self.state.model.nodes.delete(node_id=node_id)

        # 2. BLENDER
        bl_node = self.state.nodes.require_node(node_id)
        self.adapter.delete(bl_node)

        # 3. INDEX
        self.state.nodes.unregister_node(node_id)

    # ---------- REPLICATE ----------
    
    def replicate_by_vector(
        self,
        *,
        src_node_ids: list[str],
        delta: Vector,
        count: int,
    ) -> list[BlNodeObject]:

        delta_tuple = (delta.x, delta.y, delta.z)

        # 1. DOMAIN
        new_nodes = self.state.model.nodes.replicate_by_vector(
            src_node_ids=src_node_ids,
            delta=delta_tuple,
            count=count,
        )

        # 2. BLENDER
        created: list[BlNodeObject] = []

        for node in new_nodes:
            src_bl_node = self.state.nodes.require_node(node.source_id)

            bl_node = self.adapter.replicate_from(
                src_bl_node,
                node_id=node.id,
                name=f"N{node.id}",
                location=(
                    node.location.x,
                    node.location.y,
                    node.location.z,
                ),
            )

            # 3. INDEX
            self.state.nodes.register_node(node.id, bl_node)
            created.append(bl_node)

        return created
