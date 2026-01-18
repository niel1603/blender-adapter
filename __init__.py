# __init__.py

bl_info = {
    "name": "Structural object Modeler",
    "author": "Alexander Daniel P.",
    "version": (0, 1, 0),
    "blender": (5, 0, 1),
    "location": "View3D > Sidebar > SoM",
    "description": "Strcutural modeler UI",
    "category": "3D View",
}

import bpy

# -------------------------------------------------------------------
# Adapter / external bridge
# -------------------------------------------------------------------

from blender_adapter.connector.blender_connector import BlenderConnector

_adapter = BlenderConnector()
_adapter.inject_path(r"D:\COMPUTATIONAL\Python_dev")
_adapter.inject_path(r"D:\COMPUTATIONAL\Python_dev\.venv311\Lib\site-packages")

# -------------------------------------------------------------------
# Blender RNA / UI / Operators
# -------------------------------------------------------------------

from blender_adapter.core.blender_object.node import NodeRNA
from blender_adapter.core.blender_object.frame import FrameRNA

from blender_adapter.operators.start_seesion import StartSession

from blender_adapter.operators.export_json import ExportJson

from blender_adapter.operators.draw_node import DrawNode
from blender_adapter.operators.draw_frame import DrawFrame

# from blender_adapter.operators.object_move import MoveObject
# from blender_adapter.operators.object_delete import DeleteObject
# from blender_adapter.operators.object_replicate import ReplicateObject

from blender_adapter.operators.set_origin import SetOriginOperator

from blender_adapter.ui.panel_main import (
    SOM_DisplaySettings,
    SOM_PT_main_panel,
    OBJECT_PT_node_data,
)

from blender_adapter.core.app import bl_app

def _som_on_undo(scene):
    app = bl_app()
    app.drop_session(scene=scene)
    
def _som_on_redo(scene):
    app = bl_app()
    app.drop_session(scene=scene)

def _som_on_load(_dummy):
    scene = bpy.context.scene
    if scene:
        app = bl_app()
        app.drop_session(scene=scene)

BLENDER_CLASSES = (
    NodeRNA,
    FrameRNA,

    StartSession,

    ExportJson,

    DrawNode, 
    DrawFrame,

    # MoveObject,
    # DeleteObject,
    # ReplicateObject,

    SetOriginOperator,

    SOM_DisplaySettings,
    SOM_PT_main_panel,
    OBJECT_PT_node_data,

)

# -------------------------------------------------------------------
# Runtime services (handlers, bridges, overlays, etc.)
# -------------------------------------------------------------------

from blender_adapter.service.label.base import ServiceRegistry
from blender_adapter.service.label.node import NodeLabel
from blender_adapter.service.label.frame import FrameLabel

services = ServiceRegistry()
services.add(NodeLabel())
services.add(FrameLabel())

# -------------------------------------------------------------------
# Registration
# -------------------------------------------------------------------

def register():
    # 1. Register Blender-managed classes
    for cls in BLENDER_CLASSES:
        bpy.utils.register_class(cls)

    # 2. Attach RNA properties
    bpy.types.Object.node_rna = bpy.props.PointerProperty(type=NodeRNA)
    bpy.types.Object.frame_rna = bpy.props.PointerProperty(type=FrameRNA)
    bpy.types.Scene.som_display = bpy.props.PointerProperty(
        type=SOM_DisplaySettings
    )

    # 3. Enable runtime services
    services.enable_all()

    # 4. Runtime handlers (NEW)
    bpy.app.handlers.undo_post.append(_som_on_undo)
    bpy.app.handlers.redo_post.append(_som_on_redo)
    bpy.app.handlers.load_post.append(_som_on_load)

    # 5. Dev hot-reload
    try:
        _adapter.reload_development_modules()
    except Exception:
        pass

def unregister():
    # 1. Disable runtime services first
    services.disable_all()

    # 2. Remove handlers (NEW)
    if _som_on_undo in bpy.app.handlers.undo_post:
        bpy.app.handlers.undo_post.remove(_som_on_undo)
    if _som_on_redo in bpy.app.handlers.redo_post:
        bpy.app.handlers.redo_post.remove(_som_on_redo)
    if _som_on_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_som_on_load)

    # 3. Remove RNA properties
    if hasattr(bpy.types.Scene, "som_display"):
        del bpy.types.Scene.som_display

    if hasattr(bpy.types.Object, "node_rna"):
        del bpy.types.Object.node_rna

    if hasattr(bpy.types.Object, "frame_rna"):
        del bpy.types.Object.frame_rna

    # 4. Unregister Blender classes
    for cls in reversed(BLENDER_CLASSES):
        bpy.utils.unregister_class(cls)

    # 5. Disconnect external adapter
    _adapter.disconnect()
