from blender_adapter.core.blender_object.node import BlNodeAdapter
from blender_adapter.core.blender_object.frame import BlFrameAdapter

def is_plain_empty(obj) -> bool:
    """
    EMPTY object that is NOT a Node
    """
    if obj.type != 'EMPTY':
        return False

    # exclude node
    return BlNodeAdapter.get_by_object(obj) is None

def is_plain_mesh(obj) -> bool:
    """
    MESH object that is NOT a Frame
    """
    if obj.type != 'MESH' or obj.data is None:
        return False

    # exclude frame
    return BlFrameAdapter.get_by_object(obj) is None
