from blender_adapter.crud.node import BlenderNodeAdapter
from blender_adapter.crud.frame import BlenderFrameAdapter

def is_plain_empty(obj) -> bool:
    """
    EMPTY object that is NOT a Node
    """
    if obj.type != 'EMPTY':
        return False

    # exclude node
    return BlenderNodeAdapter.get_by_object(obj) is None

def is_plain_mesh(obj) -> bool:
    """
    MESH object that is NOT a Frame
    """
    if obj.type != 'MESH' or obj.data is None:
        return False

    # exclude frame
    return BlenderFrameAdapter.get_by_object(obj) is None
