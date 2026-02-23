import bpy
from mathutils import Vector
from blender_adapter.core.app import bl_app
from blender_adapter.service.preview import ClonePreview

class ReplicateObject(bpy.types.Operator):
    bl_idname = "som.replicate_object"
    bl_label = "Replicate Object"
    bl_options = {'REGISTER', 'UNDO'}

    dx: bpy.props.FloatProperty(name="ΔX", default=0.0, options={'SKIP_SAVE'})  # type: ignore
    dy: bpy.props.FloatProperty(name="ΔY", default=0.0, options={'SKIP_SAVE'})  # type: ignore
    dz: bpy.props.FloatProperty(name="ΔZ", default=0.0, options={'SKIP_SAVE'})  # type: ignore
    count: bpy.props.IntProperty(name="Count", default=1, min=1)  # type: ignore

    _preview: "ClonePreview"
    _selection: list[bpy.types.Object]

    # -------------------------------------------------
    # POLL
    # -------------------------------------------------

    @classmethod
    def poll(cls, context):
        app = bl_app()

        if not context.selected_objects:
            return False

        session = app.get_session(context.scene)
        if session is None:
            return False

        runtime = session.runtime

        for obj in context.selected_objects:
            if runtime.blender.node.get_id(obj):
                return True
            if runtime.blender.frame.get_id(obj):
                return True

        return False

    # -------------------------------------------------
    # INVOKE — SNAPSHOT + PREVIEW
    # -------------------------------------------------

    def invoke(self, context, event):
        self._selection = list(context.selected_objects)

        self._preview = ClonePreview(context, self._selection)
        self._preview.begin()

        return context.window_manager.invoke_props_dialog(self)

    # -------------------------------------------------
    # CHECK — PREVIEW UPDATE
    # -------------------------------------------------

    def check(self, context):
        delta = Vector((self.dx, self.dy, self.dz))
        offsets = [delta * i for i in range(1, self.count + 1)]

        self._preview.update(offsets)
        return True

    # -------------------------------------------------
    # EXECUTE — MUTATION SAFE
    # -------------------------------------------------

    def execute(self, context):

        self._preview.finish()

        session = bl_app().get_session(scene=context.scene)
        if session is None:
            self.report({'WARNING'}, "Session not started")
            return {'CANCELLED'}

        delta = Vector((self.dx, self.dy, self.dz))

        frame_ids: set[str] = set()
        node_ids: set[str] = set()

        for obj in self._selection:
            frame_id = session.runtime.blender.frame.get_id(obj)
            if frame_id:
                frame_ids.add(frame_id)
                continue

            node_id = session.runtime.blender.node.get_id(obj)
            if node_id:
                node_ids.add(node_id)

        # --- TRANSACTION ---

        if node_ids:
            session.ops.node.replicate_by_vector(
                src_node_ids=list(node_ids),
                delta=delta,
                count=self.count,
            )

        if frame_ids:
            session.ops.frame.replicate_by_vector(
                src_frame_ids=list(frame_ids),
                delta=delta,
                count=self.count,
            )

        return {'FINISHED'}

    # -------------------------------------------------
    # CANCEL
    # -------------------------------------------------

    def cancel(self, context):
        self._preview.finish()