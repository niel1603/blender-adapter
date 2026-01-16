import bpy
from mathutils import Vector
from blender_adapter.core.live import get_live_session
from blender_adapter.service.preview import ClonePreview

class ReplicateObject(bpy.types.Operator):
    bl_idname = "som.replicate_object"
    bl_label = "Replicate Object"
    bl_options = {'UNDO'}

    dx: bpy.props.FloatProperty(name="ΔX", default=0.0, options={'SKIP_SAVE'})  # type: ignore
    dy: bpy.props.FloatProperty(name="ΔY", default=0.0, options={'SKIP_SAVE'})  # type: ignore
    dz: bpy.props.FloatProperty(name="ΔZ", default=0.0, options={'SKIP_SAVE'})  # type: ignore
    count: bpy.props.IntProperty(name="Count", default=1, min=1) # type: ignore

    _preview_objects: list[bpy.types.Object]

    def invoke(self, context, event):
        objs = list(context.selected_objects)

        self._preview = ClonePreview(context, objs)
        self._preview.begin()

        return context.window_manager.invoke_props_dialog(self)


    def check(self, context):
        delta = Vector((self.dx, self.dy, self.dz))
        offsets = [delta * i for i in range(1, self.count + 1)]

        self._preview.update(offsets)
        return True


    def execute(self, context):
        self._preview.finish()

        session = get_live_session(context)
        delta = Vector((self.dx, self.dy, self.dz))

        src_node_ids = {
            session.model.objects.get_node_id_by_object(obj)
            for obj in context.selected_objects
            if session.model.objects.get_node_id_by_object(obj)
        }

        session.controller.nodes.replicate_by_vector(
            src_node_ids=src_node_ids,
            delta=delta,
            count=self.count,
        )

        return {'FINISHED'}


    def cancel(self, context):
        self._preview.finish()


# class ReplicateObject(bpy.types.Operator):
#     bl_idname = "som.replicate_object"
#     bl_label = "Replicate Object"
#     bl_options = {'UNDO'}

#     dx: bpy.props.FloatProperty(name="ΔX", default=0.0, options={'SKIP_SAVE'})  # type: ignore
#     dy: bpy.props.FloatProperty(name="ΔY", default=0.0, options={'SKIP_SAVE'})  # type: ignore
#     dz: bpy.props.FloatProperty(name="ΔZ", default=0.0, options={'SKIP_SAVE'})  # type: ignore
#     count: bpy.props.IntProperty(name="Count", default=1, min=1) # type: ignore

#     _preview_objects: list[bpy.types.Object]

#     # -------------------------------
#     # UI
#     # -------------------------------

#     def invoke(self, context, event):
#         self._preview_objects = []
#         return context.window_manager.invoke_props_dialog(self)

#     # -------------------------------
#     # LIVE PREVIEW (NO DOMAIN)
#     # -------------------------------

#     def check(self, context):
#         self.update_preview(context)
#         return True

#     def update_preview(self, context):
#         self.clear_preview()

#         delta = Vector((self.dx, self.dy, self.dz))
#         session = get_live_session(context)

#         for obj in context.selected_objects:
#             if obj.get("_som_preview"):
#                 continue

#             node_id = session.objects.get_node_id_by_object(obj)
#             if not node_id:
#                 continue

#             for i in range(1, self.count + 1):
#                 step = delta * i

#                 preview = obj.copy()
#                 if obj.data is not None:
#                     preview.data = obj.data.copy()

#                 preview.location = obj.location + step
#                 preview["_som_preview"] = True

#                 context.collection.objects.link(preview)
#                 preview.select_set(False)

#                 self._preview_objects.append(preview)

#     # -------------------------------
#     # EXECUTE
#     # -------------------------------

#     def execute(self, context):
#         session = get_live_session(context)
#         delta = Vector((self.dx, self.dy, self.dz))

#         src_node_ids = {
#             session.objects.get_node_id_by_object(obj)
#             for obj in context.selected_objects
#             if not obj.get("_som_preview")
#             and session.objects.get_node_id_by_object(obj)
#         }

#         self.clear_preview()

#         session.controller.nodes.replicate_by_vector(
#             src_node_ids=src_node_ids,
#             delta=delta,
#             count=self.count,
#         )

#         return {'FINISHED'}

#     # -------------------------------
#     # CANCEL / CLEANUP
#     # -------------------------------

#     def cancel(self, context):
#         self.clear_preview()

#     def clear_preview(self):
#         for obj in self._preview_objects:
#             if obj.name in bpy.data.objects:
#                 bpy.data.objects.remove(obj, do_unlink=True)
#         self._preview_objects.clear()



# class ReplicateObject(bpy.types.Operator):
#     bl_idname = "som.replicate_object"
#     bl_label = "Replicate Object"
#     bl_options = {'UNDO'}

#     dx: bpy.props.FloatProperty(name="ΔX", default=0.0, options={'SKIP_SAVE'})  # type: ignore
#     dy: bpy.props.FloatProperty(name="ΔY", default=0.0, options={'SKIP_SAVE'})  # type: ignore
#     dz: bpy.props.FloatProperty(name="ΔZ", default=0.0, options={'SKIP_SAVE'})  # type: ignore

#     count: bpy.props.IntProperty(
#         name="Count",
#         default=1,
#         min=1,
#     )  # type: ignore

#     def invoke(self, context, event):
#         return context.window_manager.invoke_props_dialog(self)

#     @classmethod
#     def poll(cls, context):
#         session = get_live_session(context)
#         return any(
#             session.objects.get_node_id_by_object(obj)
#             for obj in context.selected_objects
#         )

#     def execute(self, context):
#         delta = Vector((self.dx, self.dy, self.dz))

#         # 1. SNAPSHOT selection
#         objs = list(context.selected_objects)

#         # 2. Get live session
#         session = get_live_session(context)

#         # 3. Resolve source node IDs (deduplicated)
#         src_node_ids: list[str] = []
#         seen: set[str] = set()

#         for obj in objs:
#             node_id = session.objects.get_node_id_by_object(obj)
#             if node_id and node_id not in seen:
#                 seen.add(node_id)
#                 src_node_ids.append(node_id)

#         # 4. TRANSACTION
#         created_bl_nodes = []

#         for node_id in src_node_ids:
#             created = session.controller.nodes.replicate_by_vector(
#                 src_node_id=node_id,
#                 delta=delta,
#                 count=self.count,
#             )
#             created_bl_nodes.extend(created)
    
#         # 5. SELECTION handling
#         for obj in context.selected_objects:
#             obj.select_set(False)

#         for bl_node in created_bl_nodes:
#             bl_node.obj.select_set(True)

#         if created_bl_nodes:
#             context.view_layer.objects.active = created_bl_nodes[-1].obj

#         return {'FINISHED'}


# class ReplicateObject(bpy.types.Operator):
#     bl_idname = "som.replicate_object"
#     bl_label = "Replicate Object"
#     bl_options = {'REGISTER', 'UNDO'}

#     dx: bpy.props.FloatProperty(name="ΔX", default=0.0, options={'SKIP_SAVE'})  # type: ignore
#     dy: bpy.props.FloatProperty(name="ΔY", default=0.0, options={'SKIP_SAVE'})  # type: ignore
#     dz: bpy.props.FloatProperty(name="ΔZ", default=0.0, options={'SKIP_SAVE'})  # type: ignore

#     count: bpy.props.IntProperty(
#         name="Count",
#         default=1,
#         min=1,
#     )  # type: ignore

#     @classmethod
#     def poll(cls, context):
#         return any(
#             BlenderNodeAdapter.get_by_object(obj)
#             or BlenderFrameAdapter.get_by_object(obj)
#             for obj in context.selected_objects
#         )

#     def execute(self, context):
#         delta = Vector((self.dx, self.dy, self.dz))

#         # SNAPSHOT selection (important!)
#         source_objs = list(context.selected_objects)
#         new_objs = []

#         # BREADTH-FIRST replication (by step)
#         for i in range(1, self.count + 1):
#             step_delta = delta * i

#             for obj in source_objs:

#                 node = BlenderNodeAdapter.get_by_object(obj)
#                 if node:
#                     new_node = BlenderNodeAdapter.replicate(
#                         node,
#                         location=node.obj.location + step_delta,
#                     )
#                     new_objs.append(new_node.obj)
#                     continue

#                 frame = BlenderFrameAdapter.get_by_object(obj)
#                 if frame:
#                     new_frame = BlenderFrameAdapter.replicate(
#                         frame,
#                         direction=step_delta,
#                     )
#                     new_objs.append(new_frame.obj)

#         # ----- selection handling -----
#         for obj in new_objs:
#             obj.select_set(True)

#         if new_objs:
#             context.view_layer.objects.active = new_objs[-1]

#         return {'FINISHED'}