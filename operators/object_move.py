import bpy
from mathutils import Vector
from blender_adapter.core.live import get_live_session
from blender_adapter.service.preview import TransformPreview

class MoveObject(bpy.types.Operator):
    bl_idname = "som.move_object"
    bl_label = "Move Object"
    bl_options = {'UNDO'}

    dx: bpy.props.FloatProperty(name="ΔX", default=0.0, options={'SKIP_SAVE'})  # type: ignore
    dy: bpy.props.FloatProperty(name="ΔY", default=0.0, options={'SKIP_SAVE'})  # type: ignore
    dz: bpy.props.FloatProperty(name="ΔZ", default=0.0, options={'SKIP_SAVE'})  # type: ignore

    _original_locations: dict[bpy.types.Object, Vector]

    def invoke(self, context, event):
        objs = list(context.selected_objects)

        self._preview = TransformPreview(objs)
        self._preview.begin()

        return context.window_manager.invoke_props_dialog(self)


    def check(self, context):
        delta = Vector((self.dx, self.dy, self.dz))
        self._preview.update(delta)
        return True


    def execute(self, context):
        self._preview.finish()

        session = get_live_session(context)
        direction = (self.dx, self.dy, self.dz)

        for obj in context.selected_objects:
            node_id = session.state.identity.get_node_id_by_object(obj)
            if node_id:
                session.ops.nodes.move(
                    node_id=node_id,
                    direction=direction,
                )

        return {'FINISHED'}


    def cancel(self, context):
        self._preview.finish()

# class MoveObject(bpy.types.Operator):
#     bl_idname = "som.move_object"
#     bl_label = "Move Object"
#     bl_options = {'UNDO'}

#     dx: bpy.props.FloatProperty(name="ΔX", default=0.0, options={'SKIP_SAVE'})  # type: ignore
#     dy: bpy.props.FloatProperty(name="ΔY", default=0.0, options={'SKIP_SAVE'})  # type: ignore
#     dz: bpy.props.FloatProperty(name="ΔZ", default=0.0, options={'SKIP_SAVE'})  # type: ignore

#     _original_locations: dict[bpy.types.Object, Vector]

#     # -------------------------------
#     # POLL
#     # -------------------------------

#     @classmethod
#     def poll(cls, context):
#         session = get_live_session(context)
#         return any(
#             session.objects.get_node_id_by_object(obj)
#             for obj in context.selected_objects
#         )

#     # -------------------------------
#     # INVOKE
#     # -------------------------------

#     def invoke(self, context, event):
#         # Snapshot original transforms
#         self._original_locations = {
#             obj: obj.location.copy()
#             for obj in context.selected_objects
#             if not obj.get("_som_preview")
#         }
#         return context.window_manager.invoke_props_dialog(self)

#     # -------------------------------
#     # LIVE PREVIEW
#     # -------------------------------

#     def check(self, context):
#         self.update_preview()
#         return True

#     def update_preview(self):
#         delta = Vector((self.dx, self.dy, self.dz))

#         # Restore first (important!)
#         for obj, loc in self._original_locations.items():
#             if obj.name in bpy.data.objects:
#                 obj.location = loc

#         # Apply preview offset
#         for obj in self._original_locations:
#             obj.location += delta

#     # -------------------------------
#     # EXECUTE
#     # -------------------------------

#     def execute(self, context):
#         # Restore Blender state before domain mutation
#         for obj, loc in self._original_locations.items():
#             if obj.name in bpy.data.objects:
#                 obj.location = loc

#         direction = (self.dx, self.dy, self.dz)
#         session = get_live_session(context)

#         node_ids: set[str] = set()
#         for obj in self._original_locations:
#             node_id = session.objects.get_node_id_by_object(obj)
#             if node_id:
#                 node_ids.add(node_id)

#         # Domain transaction
#         for node_id in node_ids:
#             session.controller.nodes.move(
#                 node_id=node_id,
#                 direction=direction,
#             )

#         return {'FINISHED'}

#     # -------------------------------
#     # CANCEL
#     # -------------------------------

#     def cancel(self, context):
#         for obj, loc in self._original_locations.items():
#             if obj.name in bpy.data.objects:
#                 obj.location = loc

# class MoveObject(bpy.types.Operator):
#     bl_idname = "som.move_object"
#     bl_label = "Move Object"
#     bl_options = {'REGISTER', 'UNDO'}

#     dx: bpy.props.FloatProperty(name="ΔX", default=0.0, options={'SKIP_SAVE'})  # type: ignore
#     dy: bpy.props.FloatProperty(name="ΔY", default=0.0, options={'SKIP_SAVE'})  # type: ignore
#     dz: bpy.props.FloatProperty(name="ΔZ", default=0.0, options={'SKIP_SAVE'})  # type: ignore


#     @classmethod
#     def poll(cls, context):
#         session = get_live_session(context)
#         return any(
#             session.objects.get_node_id_by_object(obj)
#             for obj in context.selected_objects
#         )

#     def execute(self, context):
#         direction = (self.dx, self.dy, self.dz)

#         # 1. SNAPSHOT selection
#         objs = list(context.selected_objects)

#         # 2. Get live session
#         session = get_live_session(context)

#         # 3. Resolve node IDs (deduplicated)
#         node_ids: set[str] = set()
#         for obj in objs:
#             node_id = session.objects.get_node_id_by_object(obj)
#             if node_id:
#                 node_ids.add(node_id)

#         # 4. TRANSACTION (domain-first, blender-second)
#         for node_id in node_ids:
#             session.controller.nodes.move(
#                 node_id=node_id,
#                 direction=direction,
#             )

#         return {'FINISHED'}


# class MoveObject(bpy.types.Operator):
#     bl_idname = "som.move_object"
#     bl_label = "Move Object"
#     bl_options = {'REGISTER', 'UNDO'}

#     dx: bpy.props.FloatProperty(name="ΔX", default=0.0, options={'SKIP_SAVE'})  # type: ignore
#     dy: bpy.props.FloatProperty(name="ΔY", default=0.0, options={'SKIP_SAVE'})  # type: ignore
#     dz: bpy.props.FloatProperty(name="ΔZ", default=0.0, options={'SKIP_SAVE'})  # type: ignore

#     @classmethod
#     def poll(cls, context):
#         return any(
#             BlenderNodeAdapter.get_by_object(obj)
#             or BlenderFrameAdapter.get_by_object(obj)
#             for obj in context.selected_objects
#         )

#     def execute(self, context):
#         direction = (self.dx, self.dy, self.dz)

#         # snapshot selection
#         for obj in list(context.selected_objects):

#             node = BlenderNodeAdapter.get_by_object(obj)
#             if node:
#                 BlenderNodeAdapter.move(node, direction)
#                 continue

#             frame = BlenderFrameAdapter.get_by_object(obj)
#             if frame:
#                 BlenderFrameAdapter.move(frame, direction)

#         return {'FINISHED'}
