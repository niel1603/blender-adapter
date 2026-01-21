import bpy
import json
from bpy.types import Operator
from bpy.props import StringProperty
from bpy_extras.io_utils import ExportHelper

from blender_adapter.core.app import bl_app

class ExportJson(Operator, ExportHelper):
    """Export current StructuralModel to JSON"""

    bl_idname = "structural.debug_export_json"
    bl_label = "Export JSON"
    bl_options = {"REGISTER"}

    filename_ext = ".json"
    filter_glob: StringProperty(
        default="*.json",
        options={"HIDDEN"},
    ) # type: ignore

    def execute(self, context):
        
        session = bl_app().session(scene=context.scene)

        try:
            session.runtime.structural.save_json(self.filepath)
        except Exception as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}

        self.report({"INFO"}, f"Structural model exported to {self.filepath}")
        return {"FINISHED"}