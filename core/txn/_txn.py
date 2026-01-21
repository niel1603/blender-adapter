from blender_adapter.core.txn.node import BlNodeTxn
from blender_adapter.core.txn.frame import BlFrameTxn

class BlModelTxn:
    """
    Application operations façade.
    Binds transaction scripts to adapters.
    """

    def __init__(self, *, runtime):
        self.node = BlNodeTxn(runtime=runtime)
        self.frame = BlFrameTxn(runtime=runtime)