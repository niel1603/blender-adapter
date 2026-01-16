from mathutils import Vector
from structural_om.domain.model import StructuralModel 
from structural_om.domain.object import Node

from blender_adapter.core.object.node import BlenderNode
from blender_adapter.core.collection import BlenderObjectCollection
from blender_adapter.core.adapter.node import BlenderNodeAdapter

class BlenderNodeManager:

    def __init__(self, *, model, objects, adapter):
        self.model   : StructuralModel         = model
        self.objects : BlenderObjectCollection = objects
        self.adapter : BlenderNodeAdapter      = adapter

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
        node = self.model.get_or_create_node(tuple(location))
        node_id = node.id

        # 2. BLENDER (idempotent)
        bl_node = self.objects.get_node(node_id)
        if bl_node is None:
            bl_node = self.adapter.create(
                node_id=node_id,
                name=f"N{node_id}",
                location=node.xyz,
                size=size,
            )
            # 3. INDEX
            self.objects.register_node(node_id, bl_node)

        return bl_node

    # ---------- MOVE ----------

    def move(self, *, node_id, direction):
        node = self.model.nodes[node_id]

        # domain
        node.xyz = tuple(
            node.xyz[i] + direction[i] for i in range(3)
        )

        # blender
        bl_node = self.objects.require_node(node_id)
        self.adapter.move(bl_node, direction)

    # ---------- SET LOCATION (drag commit) ----------

    def set_location(self, *, node_id, location):
        node = self.model.nodes[node_id]
        node.xyz = location

        bl_node = self.objects.require_node(node_id)
        self.adapter.set_location(bl_node, location)

    # ---------- DELETE ----------

    def delete(self, *, node_id):
        
        # 1. DOMAIN
        self.model.delete_node(node_id=node_id)

        # 2. BLENDER
        bl_node = self.objects.require_node(node_id)
        self.adapter.delete(bl_node)

        self.objects.unregister_node(node_id)

    # ---------- REPLICATE ----------

    def replicate_by_vector(
        self,
        *,
        src_node_ids: list[str],
        delta: Vector,
        count: int,
    ) -> list[BlenderNode]:

        created: list[BlenderNode] = []

        src_nodes = [self.model.nodes[nid] for nid in src_node_ids]
        src_bl_nodes = [self.objects.require_node(nid) for nid in src_node_ids]

        for step in range(1, count + 1):
            step_delta = delta * step

            for src_node, src_bl_node in zip(src_nodes, src_bl_nodes):
                new_xyz = tuple(
                    src_node.xyz[i] + step_delta[i]
                    for i in range(3)
                )

                # 1. DOMAIN
                new_node_id = self.model.node_ids.allocate()
                new_node = Node(new_node_id, new_xyz)
                self.model.nodes[new_node_id] = new_node

                # 2. BLENDER
                bl_node = self.adapter.replicate_from(
                    src_bl_node,
                    node_id=new_node_id,
                    name=f"N{new_node_id}",
                    location=new_xyz,
                )

                # 3. INDEX
                self.objects.register_node(new_node_id, bl_node)

                created.append(bl_node)

        return created

    # def replicate_by_vector(
    #     self,
    #     *,
    #     src_node_id: str,
    #     delta: Vector,
    #     count: int,
    # ) -> list[BlenderNode]:

    #     src_node = self.model.nodes[src_node_id]
    #     src_bl_node = self.objects.require_node(src_node_id)

    #     created: list[BlenderNode] = []

    #     for i in range(1, count + 1):
    #         step_delta = delta * i
    #         new_xyz = tuple(
    #             src_node.xyz[j] + step_delta[j] for j in range(3)
    #         )

    #         # 1. DOMAIN
    #         new_node_id = self.model.node_ids.allocate()
    #         new_node = Node(new_node_id, new_xyz)
    #         self.model.nodes[new_node_id] = new_node

    #         # 2. BLENDER
    #         bl_node = self.adapter.replicate_from(
    #             src_bl_node,
    #             node_id=new_node_id,
    #             name=f"N{new_node_id}",
    #             location=new_xyz,
    #         )

    #         # 3. INDEX
    #         self.objects.register_node(new_node_id, bl_node)

    #         created.append(bl_node)

    #     return created
