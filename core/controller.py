from blender_adapter.core.manager.node import BlenderNodeManager

class BlenderModelController:

    def __init__(
        self,
        *,
        structural_model,
        object_collection,
        node_adapter,
    ):
        self.nodes = BlenderNodeManager(
            model=structural_model,
            objects=object_collection,
            adapter=node_adapter,
        )