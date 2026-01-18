from blender_adapter.core.ops.node import BlNodeTxn
from blender_adapter.core.blender_object.node import BlNodeAdapter

from blender_adapter.core.ops.frame import BlFrameTxn
from blender_adapter.core.blender_object.frame import BlFrameAdapter

class BlModelOps:
    """
    Application operations façade.
    Binds transaction scripts to adapters.
    """

    def __init__(self, *, state):
        self.nodes = BlNodeTxn(
            state=state,
            adapter=BlNodeAdapter,
        )

        self.frames = BlFrameTxn(
            state=state,
            adapter=BlFrameAdapter,
        )