import bpy
from mathutils import Vector
from blender_adapter.core.object.node import BlenderNode

class BlenderNodeAdapter:

    @staticmethod
    def create(*, node_id, name, location, size, collection=None) -> BlenderNode:
        if collection is None:
            collection = bpy.context.scene.collection

        obj = bpy.data.objects.new(name, None)
        obj.empty_display_type = 'PLAIN_AXES'
        obj.empty_display_size = size
        obj.location = location
        collection.objects.link(obj)

        rna = obj.node_rna
        rna.node_id = node_id
        rna.label = name

        return BlenderNode(obj)

    @staticmethod
    def move(node: BlenderNode, direction):
        node.obj.location += Vector(direction)

    @staticmethod
    def set_location(node: BlenderNode, location):
        node.obj.location = location

    @staticmethod
    def delete(node: BlenderNode):
        bpy.data.objects.remove(node.obj, do_unlink=True)

    @staticmethod
    def replicate_from(
        src: BlenderNode,
        *,
        node_id: str,
        name: str,
        location=None,
        collection=None,
    ) -> BlenderNode:

        src_obj = src.obj

        if location is None:
            location = src_obj.location.copy()

        if collection is None:
            collection = src_obj.users_collection[0]

        obj = bpy.data.objects.new(name, None)
        obj.empty_display_type = src_obj.empty_display_type
        obj.empty_display_size = src_obj.empty_display_size
        obj.location = location
        collection.objects.link(obj)

        rna = obj.node_rna
        rna.node_id = node_id
        rna.label = name

        return BlenderNode(obj)