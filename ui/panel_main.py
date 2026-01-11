# blender_adapter/ui/panel_main.py

import bpy

class SoM_DisplaySettings(bpy.types.PropertyGroup):
    # -------------------------
    # Node labels
    # -------------------------
    show_node_id: bpy.props.BoolProperty( # type: ignore
        name="Node ID",
        default=True
    )

    show_node_label: bpy.props.BoolProperty( # type: ignore
        name="Node Label",
        default=True
    )

    # -------------------------
    # Frame labels
    # -------------------------
    show_frame_id: bpy.props.BoolProperty( # type: ignore
        name="Frame ID",
        default=True
    )

    show_frame_label: bpy.props.BoolProperty( # type: ignore
        name="Frame Label",
        default=True
    )

class SoM_main_panel(bpy.types.Panel):
    bl_label = "Structural object Modeler"
    bl_idname = "SoM_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SoM"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        display = scene.som_display

        # -------------------------------------------------
        # Geometry operators
        # -------------------------------------------------
        layout.label(text="Geometry", icon='MESH_DATA')
        layout.operator("som.create_node_modal", icon='GREASEPENCIL')
        layout.operator("som.create_frame_modal", icon='GREASEPENCIL')

        # -------------------------------------------------
        # Transform
        # -------------------------------------------------
        layout.separator()
        layout.label(text="Transform", icon='OBJECT_ORIGIN')

        layout.operator("som.move_object", icon='EMPTY_AXIS')
        layout.operator("som.delete_object", icon='EMPTY_AXIS')
        layout.operator("som.replicate_object", icon='EMPTY_AXIS')

        layout.separator()
        layout.operator("som.set_origin_to_geometry", icon='PIVOT_MEDIAN')

        # -------------------------------------------------
        # Viewport labels
        # -------------------------------------------------
        layout.separator()
        layout.label(text="Viewport Labels", icon='FONT_DATA')

        col = layout.column(align=True)
        col.label(text="Nodes")
        col.prop(display, "show_node_id", text="ID")
        col.prop(display, "show_node_label", text="Label")

        layout.separator()

        col = layout.column(align=True)
        col.label(text="Frames")
        col.prop(display, "show_frame_id", text="ID")
        col.prop(display, "show_frame_label", text="Label")


class OBJECT_panel_node(bpy.types.Panel):
    bl_label = "Node Data"
    bl_idname = "OBJECT_PT_node_data"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"   # <-- Object tab

    def draw(self, context):
        obj = context.object
        if not obj or not hasattr(obj, "node_rna"):
            return

        rna = obj.node_rna
        layout = self.layout
        layout.prop(rna, "node_id")
        layout.prop(rna, "node_type")
        layout.prop(rna, "label")
