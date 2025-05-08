from importlib.util import LazyLoader
import bpy
from _ctypes import PyObj_FromPtr
from bpy.props import (
    StringProperty,
    BoolProperty,
)
from bpy.app.translations import (
    pgettext_iface as iface_,
    pgettext_tip as tip_,
)

COLLECTION_ICON_NAME = 'OUTLINER_COLLECTION' if 'OUTLINER_COLLECTION' \
                        in bpy.types.UILayout.bl_rna.functions[
                            'prop'].parameters['icon'].enum_items.keys() \
                        else 'GROUP'

class FINALCHECK_OT_Check(bpy.types.Operator):
    bl_idname = "finalcheck.check"
    bl_label = "Check"
    bl_description = tip_("Detect problems")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        finalCheck = context.window_manager.finalCheck
        finalCheck.check()

        if finalCheck.missingFiles or finalCheck.checkedItems:
            self.report({'WARNING'}, iface_("Problems detected"))
        else:
            self.report({'INFO'}, iface_("No problems detected"))
        return {'FINISHED'}

class FINALCHECK_OT_SetObjHide(bpy.types.Operator):
    bl_idname = "finalcheck.set_obj_hide"
    bl_label = "Hide in viewport"
    bl_description = tip_("Toggle visibility")
    bl_options = {'REGISTER', 'UNDO'}

    obj: StringProperty(
        name="obj",
        options={"HIDDEN"},
    )
    scene: StringProperty(
        name="scene",
        options={"HIDDEN"},
    )
    vl: StringProperty(
        name="vl",
        options={"HIDDEN"},
    )
    ### This def might be in top level for reuse, but causes crash...
    def ShowMessageBox(self):
        def draw(self, context):
            self.layout.label(text=iface_("This Item cannot be Changed from Other Scenes"))
        bpy.context.window_manager.popup_menu(draw, title = iface_("Toggle scene to {}").format(self.scene), icon = "HIDE_OFF")
    def execute(self, context):
        if context.scene.name != self.scene:
            self.ShowMessageBox()
            return {'FINISHED'}
        vl = bpy.data.scenes[self.scene].view_layers[self.vl]
        obj = bpy.data.scenes[self.scene].objects[self.obj]
        obj.hide_set(not obj.hide_get(view_layer=vl), view_layer=vl)
        return {'FINISHED'}

class FINALCHECK_OT_ToggleVisibilityInPanel(bpy.types.Operator):
    bl_idname = "finalcheck.toggle_visibility_in_panel"
    bl_label = "Toggle visibility"
    bl_description = tip_("Toggle visibility")
    bl_options = {'REGISTER', 'UNDO'}

    objId: StringProperty(
        name="objId",
        options={"HIDDEN"},
    )
    def execute(self, context):
        visibility = PyObj_FromPtr(int(self.objId))
        visibility["hide"] = not visibility["hide"]
        return {'FINISHED'}

class FINALCHECK_OT_ClearRenderRegion(bpy.types.Operator):
    bl_idname = "finalcheck.clear_render_region"
    bl_label = "Clear Render Region"
    bl_description = tip_("Clear Render Region")
    bl_options = {'REGISTER', 'UNDO'}

    objId: StringProperty(
        name="objId",
        options={"HIDDEN"},
    )
    def execute(self, context):
        renderSettings = PyObj_FromPtr(int(self.objId))
        context.window_manager.finalCheck.clearRenderRegion(renderSettings)
        self.report({'INFO'}, iface_("Render Region cleared"))
        return {'FINISHED'}

class FINALCHECK_OT_SelectObject(bpy.types.Operator):
    bl_idname = "finalcheck.select_object"
    bl_label = "Select object"
    bl_description = tip_("Select object")
    bl_options = {'REGISTER', 'UNDO'}

    objName: StringProperty(
        name="objName",
        options={"HIDDEN"},
    )
    scene: StringProperty(
        name="scene",
        options={"HIDDEN"},
    )
    def ShowMessageBox(self):
        def draw(self, context):
            self.layout.label(text=iface_("Cannot select objects of ohter scene"))
        bpy.context.window_manager.popup_menu(draw, title = iface_("Toggle scene to {}").format(self.scene), icon = "ERROR")
    def execute(self, context):
        if context.scene.name != self.scene:
            self.ShowMessageBox()
            return {'FINISHED'}
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = bpy.data.objects[self.objName]
        bpy.data.objects[self.objName].select_set(True)
        return {'FINISHED'}

class FINALCHECK_OT_Render(bpy.types.Operator):
    bl_idname = "finalcheck.render"
    bl_label = "Check and Render"
    bl_description = tip_("Check problems and render if no problems exist")
    bl_options = {'REGISTER', 'UNDO'}

    animation: BoolProperty(
        name="animation",
        options={"HIDDEN", "SKIP_SAVE"},
        default=False,
    )
    write_still: BoolProperty(
        name="write_still",
        options={"HIDDEN", "SKIP_SAVE"},
        default=False,
    )
    use_viewport: BoolProperty(
        name="use_viewport",
        options={"HIDDEN", "SKIP_SAVE"},
        default=False,
    )
    layer: StringProperty(
        name="layer",
        options={"HIDDEN", "SKIP_SAVE"},
    )
    scene: StringProperty(
        name="scene",
        options={"HIDDEN", "SKIP_SAVE"},
    )
    def execute(self, context):
        finalCheck = context.window_manager.finalCheck
        finalCheck.check()

        if finalCheck.missingFiles or finalCheck.checkedItems:
            self.report({'WARNING'}, iface_("Problems detected"))
        else:
            bpy.ops.render.render('INVOKE_DEFAULT', True, 
                                    animation=self.animation,
                                    write_still=self.write_still,
                                    use_viewport=self.use_viewport,
                                    layer=self.layer,
                                    scene=self.scene)
            self.report({'INFO'}, iface_("No problems detected"))
        return {'FINISHED'}

class FinalCheckPanel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "FinalCheck" #tab name

class FINALCHECK_PT_Menu(FinalCheckPanel, bpy.types.Panel):
    bl_label = "FinalCheck" #header name

    def getObjType(self, obj):
        type = obj.type
        if type == "MESH":
            return "OUTLINER_OB_MESH"
        elif type == "CURVE":
            return "OUTLINER_OB_CURVE"
        elif type == "CURVES": # Blender 3.3 and above
            return "OUTLINER_OB_CURVES"
        elif type == "SURFACE":
            return "OUTLINER_OB_SURFACE"
        elif type == "META":
            return "OUTLINER_OB_META"
        elif type == "FONT":
            return "OUTLINER_OB_FONT"
        elif type == "HAIR":
            return "OUTLINER_OB_HAIR"
        elif type == "POINTCLOUD":
            return "OUTLINER_OB_POINTCLOUD"
        elif type == "VOLUME":
            return "OUTLINER_OB_VOLUME"
        elif type == "GPENCIL":
            return "OUTLINER_OB_GREASEPENCIL"
        elif type == "ARMATURE":
            return "OUTLINER_OB_ARMATURE"
        elif type == "LATTICE":
            return "OUTLINER_OB_LATTICE"
        elif type == "EMPTY":
            if obj.empty_display_type == "IMAGE":
                return "OUTLINER_OB_IMAGE"
            ### empty which have never been force field doesn't have field.type
            elif hasattr(obj.field, "type") and obj.field.type != "NONE":
                return "OUTLINER_OB_FORCE_FIELD"
            elif obj.instance_type == "COLLECTION":
                return "OUTLINER_OB_GROUP_INSTANCE"
            else:
                return "OUTLINER_OB_EMPTY"
        elif type == "LIGHT":
            return "OUTLINER_OB_LIGHT"
        elif type == "LIGHT_PROBE":
            return "OUTLINER_OB_LIGHTPROBE"
        elif type == "CAMERA":
            return "OUTLINER_OB_CAMERA"
        elif type == "SPEAKER":
            return "OUTLINER_OB_SPEAKER"
        else:
            return "QUESTION"
    
    def separator(self, layout, iter, fac=1):
        for _ in range(iter):
            layout.separator(factor=fac)

    def draw(self, context):
        layout = self.layout
        layout.operator(FINALCHECK_OT_Check.bl_idname, text=iface_("Check"))
        row = layout.row(align=True)
        layout.separator()
        finalCheck = context.window_manager.finalCheck
        missingFiles = finalCheck.missingFiles
        try:
            if not missingFiles and not finalCheck.checkedItems and not finalCheck.notCheckedYet:
                row = layout.row(align=True)
                row.alignment = "CENTER"
                row.label(text=iface_("No problems detected"))
                return
            if missingFiles and "files" in missingFiles:
                row = layout.row(align=True)
                row.operator(FINALCHECK_OT_ToggleVisibilityInPanel.bl_idname, text="", icon="DISCLOSURE_TRI_RIGHT" if missingFiles["hide"] else "DISCLOSURE_TRI_DOWN",emboss=False).objId = str(id(missingFiles))
                row.label(text=iface_("Missing Files"))
                if not missingFiles["hide"]:
                    for image in missingFiles["files"]:
                        row = layout.row(align=True)
                        row.separator(factor=2)
                        row.label(text=image, icon="FILE_IMAGE", translate=False)
            for scene, vls in finalCheck.checkedItems.items():
                row = layout.row(align=True)
                row.alignment="LEFT"
                row.operator(FINALCHECK_OT_ToggleVisibilityInPanel.bl_idname, text="", icon="DISCLOSURE_TRI_RIGHT" if vls["hide"] else "DISCLOSURE_TRI_DOWN",emboss=False).objId = str(id(vls))
                row.label(text=scene.name, icon="SCENE_DATA", translate=False)
                if vls["hide"]:
                    continue
                if "border" in vls.keys():
                    row = layout.row(align=True)
                    row.separator(factor=2)
                    row.label(text=iface_("Render Region is set"), icon="ERROR")
                    row.operator(FINALCHECK_OT_ClearRenderRegion.bl_idname, text=iface_("Clear")).objId = str(id(vls["border"]))
                if "resolution_percentage" in vls.keys():
                    row = layout.row(align=True)
                    row.separator(factor=2)
                    row.label(text=iface_("Resolution % is under 100%"), icon="ERROR")
                    row.prop(scene.render, "resolution_percentage")
                if "cycles_sample" in vls.keys():
                    row = layout.row(align=True)
                    row.separator(factor=2)
                    sp = row.split(align=True,factor=.5)
                    sp.label(text=iface_("Render samples are less than preview samples"), icon="ERROR")
                    sp.prop(scene.cycles, "preview_samples")
                    sp.prop(scene.cycles, "samples")
                elif "eevee_sample" in vls.keys():
                    row = layout.row(align=True)
                    row.separator(factor=2)
                    sp = row.split(align=True,factor=.5)
                    sp.label(text=iface_("Render samples are less than preview samples"), icon="ERROR")
                    sp.prop(scene.eevee, "taa_samples")
                    sp.prop(scene.eevee, "taa_render_samples")
                elif "cycles_aa_sample" in vls.keys():
                    row = layout.row(align=True)
                    row.separator(factor=2)
                    sp = row.split(align=True,factor=.5)
                    sp.label(text=iface_("Render samples are less than preview samples"), icon="ERROR")
                    sp.prop(scene.cycles, "preview_aa_samples")
                    sp.prop(scene.cycles, "aa_samples")
                if "composite" in vls.keys():
                    row = layout.row(align=True)
                    row.separator(factor=2)
                    row.label(text=iface_("Input of Composite node and Viewer node are different"), icon="ERROR")

                if "view_layers" in vls.keys():
                    for vl, colls in vls["view_layers"].items():
                        row = layout.row(align=True)
                        row.separator(factor=2)
                        row.operator(FINALCHECK_OT_ToggleVisibilityInPanel.bl_idname, text="", icon="DISCLOSURE_TRI_RIGHT" if colls["hide"] else "DISCLOSURE_TRI_DOWN",emboss=False).objId = str(id(colls))
                        row.label(text=vl.name, icon="RENDERLAYERS", translate=False)
                        # row.operator(FINALCHECK_OT_SelectObject.bl_idname, text=vl.name, icon="RENDERLAYERS", translate=False).objName = vl.name
                        if colls["hide"]:
                            continue
                        for coll, objs in colls["colls"].items():
                            row = layout.row(align=True)
                            self.separator(row, 2, 2)
                            row.operator(FINALCHECK_OT_ToggleVisibilityInPanel.bl_idname, text="", icon="DISCLOSURE_TRI_RIGHT" if objs["hide"] else "DISCLOSURE_TRI_DOWN",emboss=False).objId = str(id(objs))
                            if hasattr(coll, "collection"): #Master Collection doesn't have show/hide status.
                                row.label(text=coll.name, icon=COLLECTION_ICON_NAME, translate=False)
                                row.prop(coll, "hide_viewport", icon_only=True,emboss=False)
                                row.prop(coll.collection, "hide_viewport", icon_only=True,emboss=False)
                                row.prop(coll.collection, "hide_render", icon_only=True,emboss=False)
                            else:
                                row.label(text=iface_("Master Collection"), icon=COLLECTION_ICON_NAME)
                            if objs["hide"]:
                                continue
                            for obj, mods in objs["objs"].items():
                                # row = layout.row(align=True)
                                sp = layout.split(align=True,factor=.75)
                                row = sp.row(align=True)
                                row.alignment = "LEFT"
                                self.separator(row, 3, 2)
                                row.operator(FINALCHECK_OT_ToggleVisibilityInPanel.bl_idname, text="", icon="DISCLOSURE_TRI_RIGHT" if mods["hide"] else "DISCLOSURE_TRI_DOWN",emboss=False).objId = str(id(mods))
                                objName = row.operator(FINALCHECK_OT_SelectObject.bl_idname, text=obj.name, icon=self.getObjType(obj), translate=False, emboss=False)
                                objName.objName = obj.name
                                objName.scene = scene.name
                                row = sp.row(align=True)
                                row.alignment = "RIGHT"
                                objHide = row.operator(FINALCHECK_OT_SetObjHide.bl_idname, text="", icon="HIDE_ON" if obj.hide_get(view_layer=vl) else "HIDE_OFF",emboss=False)
                                objHide.obj = obj.name
                                objHide.scene = scene.name
                                objHide.vl = vl.name
                                row.prop(obj, "hide_viewport", icon_only=True,emboss=False)
                                row.prop(obj, "hide_render", icon_only=True,emboss=False)
                                if mods["hide"]:
                                    continue
                                if "instance" in mods.keys():
                                    row = layout.row(align=True)
                                    self.separator(row, 4, 2)
                                    row.label(icon="DOT")
                                    row.label(text=iface_("Instancing"), icon="MOD_INSTANCE")
                                    row.prop(obj, "show_instancer_for_viewport", icon_only=True, icon="RESTRICT_VIEW_OFF" if obj.show_instancer_for_viewport else "RESTRICT_VIEW_ON",emboss=False)
                                    row.prop(obj, "show_instancer_for_render", icon_only=True, icon="RESTRICT_RENDER_OFF" if obj.show_instancer_for_render else "RESTRICT_RENDER_ON",emboss=False)
                                for mod, value in mods["mods"].items():
                                    row = layout.row(align=True)
                                    self.separator(row, 4, 2)
                                    row.operator(FINALCHECK_OT_ToggleVisibilityInPanel.bl_idname, text="", icon="DISCLOSURE_TRI_RIGHT" if value["hide"] else "DISCLOSURE_TRI_DOWN",emboss=False).objId = str(id(value))
                                    row.label(text=mod.name, icon="MODIFIER", translate=False)
                                    row.prop(mod, "show_viewport", icon_only=True,emboss=False)
                                    row.prop(mod, "show_render", icon_only=True,emboss=False)
                                    if value["hide"]:
                                        continue
                                    if "show_emitter" in value:
                                        row = layout.row(align=True)
                                        self.separator(row, 5, 2)
                                        row.label(icon="DOT")
                                        row.label(text=iface_("Show Emitter"), icon="PARTICLES")
                                        row.prop(value["show_emitter"], "show_instancer_for_viewport", icon="RESTRICT_VIEW_OFF" if obj.show_instancer_for_viewport else "RESTRICT_VIEW_ON", icon_only=True,emboss=False)
                                        row.prop(value["show_emitter"], "show_instancer_for_render", icon="RESTRICT_RENDER_OFF" if obj.show_instancer_for_render else "RESTRICT_RENDER_ON", icon_only=True,emboss=False)
                                    if "child_amount" in value:
                                        row = layout.row(align=True)
                                        self.separator(row, 5, 2)
                                        row.label(icon="DOT")
                                        row.label(text=iface_("Child Amount"), icon="PARTICLES")
                                        if (4, 0, 0) > bpy.app.version:
                                            row.prop(value["child_amount"], "child_nbr")
                                        else:
                                            row.prop(value["child_amount"], "child_percent")
                                        row.prop(value["child_amount"], "rendered_child_count")
                                    if "display_percentage" in value:
                                        row = layout.row(align=True)
                                        self.separator(row, 5, 2)
                                        row.label(icon="DOT")
                                        row.label(text=iface_("Viewport Display Amount"), icon="PARTICLES")
                                        row.prop(value["display_percentage"], "display_percentage")
                                for gpfx, value in mods["gpfxs"].items():
                                    row = layout.row(align=True)
                                    self.separator(row, 4, 2)
                                    row.label(icon="DOT")
                                    row.label(text=gpfx.name, icon="MODIFIER", translate=False)
                                    row.prop(gpfx, "show_viewport", icon_only=True,emboss=False)
                                    row.prop(gpfx, "show_render", icon_only=True,emboss=False)
                                for fx, value in mods["fxs"].items():
                                    row = layout.row(align=True)
                                    self.separator(row, 4, 2)
                                    row.label(icon="DOT")
                                    row.label(text=fx.name, icon="SHADERFX", translate=False)
                                    row.prop(fx, "show_viewport", icon_only=True,emboss=False)
                                    row.prop(fx, "show_render", icon_only=True,emboss=False)
        except ReferenceError:
            row = layout.row(align=True)
            row.alignment = "CENTER"
            row.alert=True
            row.label(text=iface_("Outdated Data: Please check again"))

class FINALCHECK_PT_Menu_Prefs(FinalCheckPanel, bpy.types.Panel):
    bl_parent_id = "FINALCHECK_PT_Menu"
    bl_label = iface_("Preferences")

    def getName(self, prop):
        try:
            name = prop.keywords['name']
        except AttributeError: # blender 2.92 or before
            name = prop[1]['name']
        return iface_(name)

    def draw(self, context):
        wm = context.window_manager
        types = bpy.types.WindowManager
        layout = self.layout
        layout.label(text=iface_("Check"))
        box = layout.box()
        box.prop(wm, "finalCheck_prefs_autoCheck", text=self.getName(types.finalCheck_prefs_autoCheck))
        box.prop(wm, "finalCheck_prefs_currentScene", text=self.getName(types.finalCheck_prefs_currentScene))
        row = box.row()
        if not wm.finalCheck_prefs_currentScene:
            row.active = False
        row.separator()
        row.prop(wm, "finalCheck_prefs_currentViewLayer", text=self.getName(types.finalCheck_prefs_currentViewLayer))

        layout.label(text=iface_("Check These Statues"))
        box = layout.box()
        box.prop(wm, "finalCheck_prefs_collVisibility", text=self.getName(types.finalCheck_prefs_collVisibility))
        box.prop(wm, "finalCheck_prefs_objVisibility", text=self.getName(types.finalCheck_prefs_objVisibility))
        box.prop(wm, "finalCheck_prefs_missingFiles", text=self.getName(types.finalCheck_prefs_missingFiles))
        box.prop(wm, "finalCheck_prefs_renderRegion", text=self.getName(types.finalCheck_prefs_renderRegion))
        box.prop(wm, "finalCheck_prefs_resolutionPercentage", text=self.getName(types.finalCheck_prefs_resolutionPercentage))
        box.prop(wm, "finalCheck_prefs_samples", text=self.getName(types.finalCheck_prefs_samples))
        box.prop(wm, "finalCheck_prefs_instance", text=self.getName(types.finalCheck_prefs_instance))
        box.prop(wm, "finalCheck_prefs_modifiers", text=self.getName(types.finalCheck_prefs_modifiers))
        row = box.row()
        row.alignment = "LEFT"
        row.prop(wm, "finalCheck_prefs_composite", text=self.getName(types.finalCheck_prefs_composite))
        row.label(text=iface_("(α Ver.)"))

        box.label(text=iface_("Particles"))
        row = box.row()
        row.separator(factor=1)
        row.prop(wm, "finalCheck_prefs_particleShowEmitter", text=self.getName(types.finalCheck_prefs_particleShowEmitter))
        row = box.row()
        row.separator(factor=1)
        row.prop(wm, "finalCheck_prefs_particleChildAmount", text=self.getName(types.finalCheck_prefs_particleChildAmount))
        row = box.row()
        row.separator(factor=1)
        row.prop(wm, "finalCheck_prefs_particleDisplayPercentage", text=self.getName(types.finalCheck_prefs_particleDisplayPercentage))
        box.label(text=iface_("Grease Pencil"))
        row = box.row()
        row.separator(factor=1)
        if (4, 3, 0) > bpy.app.version:
            row.prop(wm, "finalCheck_prefs_gpencilModifiers", text=self.getName(types.finalCheck_prefs_gpencilModifiers))
            row = box.row()
            row.separator(factor=1)
        row.prop(wm, "finalCheck_prefs_gpencilShaderEffects", text=self.getName(types.finalCheck_prefs_gpencilShaderEffects))