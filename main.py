from pprint import pprint 
import bpy
from _ctypes import PyObj_FromPtr
from . import attenRenClass
from bpy.props import (
    PointerProperty,
    BoolProperty,
    StringProperty,
    IntProperty,
)



class ATTENREN_OT_Check(bpy.types.Operator):
    bl_idname = "attenren.check"
    bl_label = "Check"
    bl_description = bpy.app.translations.pgettext("Detect Problems")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.window_manager.attenRen.checkedItems.clear()
        context.window_manager.attenRen.missingFiles.clear()
        context.window_manager.attenRen.check()
        return {'FINISHED'}

class ATTENREN_OT_SetObjHide(bpy.types.Operator):
    bl_idname = "attenren.set_obj_hide"
    bl_label = "Toggle Object"
    bl_description = bpy.app.translations.pgettext("Toggle Visibility")
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
    ### This def should be in top level for reuse, but causes crash...
    def ShowMessageBox(self):
        def draw(self, context):
            self.layout.label(text=bpy.app.translations.pgettext("This Item cannot be Changed from Other Scenes"))
        bpy.context.window_manager.popup_menu(draw, title = bpy.app.translations.pgettext("Toggle Scene to {}").format(self.scene), icon = "HIDE_OFF")
    def execute(self, context):
        if context.scene.name != self.scene:
            self.ShowMessageBox()
            return {'FINISHED'}
        vl = bpy.data.scenes[self.scene].view_layers[self.vl]
        obj = bpy.data.scenes[self.scene].objects[self.obj]
        obj.hide_set(not obj.hide_get(view_layer=vl), view_layer=vl)
        return {'FINISHED'}

class ATTENREN_OT_MatchVisibility(bpy.types.Operator):
    bl_idname = "attenren.match_visibility"
    bl_label = "Match Visibility"
    bl_description = bpy.app.translations.pgettext("Match Visibility of All Collections, Objects, Modifiers and Effects to Viewport/Render")
    bl_options = {'REGISTER', 'UNDO'}

    matchTo: StringProperty(
        name="to",
        options={"HIDDEN"},
    )
    def execute(self, context):
        context.window_manager.attenRen.matchVisibility(self.matchTo)
        return {'FINISHED'}

class ATTENREN_OT_ToggleVisibilityInPanel(bpy.types.Operator):
    bl_idname = "attenren.toggle_visibility_in_panel"
    bl_label = "Toggle Visibility"
    bl_description = bpy.app.translations.pgettext("Toggle Visibility")
    bl_options = {'REGISTER', 'UNDO'}

    objId: StringProperty(
        name="objId",
        options={"HIDDEN"},
    )
    def execute(self, context):
        visibility = PyObj_FromPtr(int(self.objId))
        visibility["hide"] = not visibility["hide"]
        return {'FINISHED'}

class ATTENREN_OT_ClearRenderRegion(bpy.types.Operator):
    bl_idname = "attenren.clear_render_region"
    bl_label = "Clear Render Region"
    bl_description = bpy.app.translations.pgettext("Clear Render Region")
    bl_options = {'REGISTER', 'UNDO'}

    objId: StringProperty(
        name="objId",
        options={"HIDDEN"},
    )
    def execute(self, context):
        renderSettings = PyObj_FromPtr(int(self.objId))
        context.window_manager.attenRen.clearRenderRegion(renderSettings)
        return {'FINISHED'}

class AttenRenPanel:
    bl_space_type = 'VIEW_3D'           # パネルを登録するスペース
    bl_region_type = 'UI'               # パネルを登録するリージョン
    bl_category = "AttentiveRendering"        # パネルを登録するタブ名

class ATTENREN_PT_Menu(AttenRenPanel, bpy.types.Panel):
    bl_label = "AttentiveRendering"         # パネルのヘッダに表示される文字列
    bl_idname = "ATTENREN_PT_Menu"

    def getObjType(self, obj):
        type = obj.type
        if type == "MESH":
            return "OUTLINER_OB_MESH"
        elif type == "CURVE":
            return "OUTLINER_OB_CURVE"
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
            elif not obj.field.type == "NONE":
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


    def draw(self, context):
        layout = self.layout
        layout.operator(ATTENREN_OT_Check.bl_idname, text=bpy.app.translations.pgettext("Check"))
        row = layout.row(align=True)
        row.operator(ATTENREN_OT_MatchVisibility.bl_idname, text=bpy.app.translations.pgettext("Match To Viewport")).matchTo = "VIEWPORT"
        row.operator(ATTENREN_OT_MatchVisibility.bl_idname, text=bpy.app.translations.pgettext("Match To Render")).matchTo = "RENDER"
        layout.separator()
        attenRen = context.window_manager.attenRen
        missingFiles = attenRen.missingFiles
        if missingFiles and missingFiles["files"]:
            row = layout.row(align=True)
            row.operator(ATTENREN_OT_ToggleVisibilityInPanel.bl_idname, text="", icon="DISCLOSURE_TRI_RIGHT" if missingFiles["hide"] else "DISCLOSURE_TRI_DOWN",emboss=False).objId = str(id(missingFiles))
            row.label(text=bpy.app.translations.pgettext("Missing Files"))
            if not missingFiles["hide"]:
                for image in missingFiles["files"]:
                    row = layout.row(align=True)
                    row.separator(factor=2)
                    row.label(text=image, icon="FILE_IMAGE")
        for scene, vls in attenRen.checkedItems.items():
            row = layout.row(align=True)
            row.alignment="LEFT"
            # row.label(text="｜")
            row.operator(ATTENREN_OT_ToggleVisibilityInPanel.bl_idname, text="", icon="DISCLOSURE_TRI_RIGHT" if vls["hide"] else "DISCLOSURE_TRI_DOWN",emboss=False).objId = str(id(vls))
            row.label(text=scene.name, icon="SCENE_DATA")
            if vls["hide"]:
                continue
            if "border" in vls.keys():
                row = layout.row(align=True)
                row.separator(factor=2)
                row.label(text=bpy.app.translations.pgettext("Render Region is Set"), icon="ERROR")
                row.operator(ATTENREN_OT_ClearRenderRegion.bl_idname, text=bpy.app.translations.pgettext("Clear")).objId = str(id(vls["border"]))
            if "resolution_percentage" in vls.keys():
                row = layout.row(align=True)
                row.separator(factor=2)
                row.label(text=bpy.app.translations.pgettext("Resolution % is under 100%"), icon="ERROR")
                row.prop(scene.render, "resolution_percentage")
            if "cycles_sample" in vls.keys():
                row = layout.row(align=True)
                row.separator(factor=2)
                sp = row.split(align=True,factor=0.5)
                sp.label(text=bpy.app.translations.pgettext("Render Samples are Less than Preview Samples"), icon="ERROR")
                sp.prop(scene.cycles, "samples")
                sp.prop(scene.cycles, "preview_samples")
            elif "eevee_sample" in vls.keys():
                row = layout.row(align=True)
                row.separator(factor=2)
                sp = row.split(align=True,factor=0.5)
                sp.label(text=bpy.app.translations.pgettext("Render Samples are Less than Preview Samples"), icon="ERROR")
                sp.prop(scene.eevee, "taa_render_samples")
                sp.prop(scene.eevee, "taa_samples")
            elif "cycles_aa_sample" in vls.keys():
                row = layout.row(align=True)
                row.separator(factor=2)
                sp = row.split(align=True,factor=0.5)
                sp.label(text=bpy.app.translations.pgettext("Render Samples are Less than Preview Samples"), icon="ERROR")
                sp.prop(scene.cycles, "aa_samples")
                sp.prop(scene.cycles, "preview_aa_samples")
            if "composite" in vls.keys():
                row = layout.row(align=True)
                row.separator(factor=2)
                row.label(text=bpy.app.translations.pgettext("Input Sources of Composite Output and Viewer Output are Different"), icon="ERROR")

            for vl, colls in vls["view_layers"].items():
                row = layout.row(align=True)
                row.separator(factor=2)
                # row.separator_spacer()
                row.operator(ATTENREN_OT_ToggleVisibilityInPanel.bl_idname, text="", icon="DISCLOSURE_TRI_RIGHT" if colls["hide"] else "DISCLOSURE_TRI_DOWN",emboss=False).objId = str(id(colls))
                row.label(text=vl.name, icon="RENDERLAYERS")
                if colls["hide"]:
                    continue
                for i, (coll, objs) in enumerate(colls["colls"].items()):
                    row = layout.row(align=True)
                    row.separator(factor=2)
                    row.separator(factor=2)
                    # row.separator_spacer()
                    # row.separator_spacer()
                    row.operator(ATTENREN_OT_ToggleVisibilityInPanel.bl_idname, text="", icon="DISCLOSURE_TRI_RIGHT" if objs["hide"] else "DISCLOSURE_TRI_DOWN",emboss=False).objId = str(id(objs))
                    row.label(text=coll.name, icon="OUTLINER_COLLECTION")
                    if hasattr(coll, "collection"): #Omit Master Collection because it doesn't have show/hide status.
                        row.prop(coll, "hide_viewport", icon_only=True,emboss=False)
                        row.prop(coll.collection, "hide_viewport", icon_only=True,emboss=False)
                        row.prop(coll.collection, "hide_render", icon_only=True,emboss=False)
                    if objs["hide"]:
                        continue
                    for obj, mods in objs["objs"].items():
                        row = layout.row(align=True)
                        row.separator(factor=2)
                        row.separator(factor=2)
                        row.separator(factor=2)
                        # row.separator_spacer()
                        row.operator(ATTENREN_OT_ToggleVisibilityInPanel.bl_idname, text="", icon="DISCLOSURE_TRI_RIGHT" if mods["hide"] else "DISCLOSURE_TRI_DOWN",emboss=False).objId = str(id(mods))
                        row.label(text=obj.name, icon=self.getObjType(obj))
                        objHide = row.operator(ATTENREN_OT_SetObjHide.bl_idname, text="", icon="HIDE_ON" if obj.hide_get(view_layer=vl) else "HIDE_OFF",emboss=False)
                        objHide.obj = obj.name
                        objHide.scene = scene.name
                        objHide.vl = vl.name
                        row.prop(obj, "hide_viewport", icon_only=True,emboss=False)
                        row.prop(obj, "hide_render", icon_only=True,emboss=False)
                        if mods["hide"]:
                            continue
                        if "instance" in mods.keys():
                            row = layout.row(align=True)
                            row.separator(factor=2)
                            row.separator(factor=2)
                            row.separator(factor=2)
                            row.separator(factor=2)
                            row.label(icon="DOT")
                            row.label(text=bpy.app.translations.pgettext("Instancing"), icon="MOD_INSTANCE")
                            row.prop(obj, "show_instancer_for_viewport", icon_only=True, icon="RESTRICT_VIEW_OFF" if obj.show_instancer_for_viewport else "RESTRICT_VIEW_ON",emboss=False)
                            row.prop(obj, "show_instancer_for_render", icon_only=True, icon="RESTRICT_RENDER_OFF" if obj.show_instancer_for_render else "RESTRICT_RENDER_ON",emboss=False)
                        for mod, value in mods["mods"].items():
                            row = layout.row(align=True)
                            row.separator(factor=2)
                            row.separator(factor=2)
                            row.separator(factor=2)
                            row.separator(factor=2)
                            row.operator(ATTENREN_OT_ToggleVisibilityInPanel.bl_idname, text="", icon="DISCLOSURE_TRI_RIGHT" if value["hide"] else "DISCLOSURE_TRI_DOWN",emboss=False).objId = str(id(value))
                            row.label(text=mod.name, icon="MODIFIER")
                            row.prop(mod, "show_viewport", icon_only=True,emboss=False)
                            row.prop(mod, "show_render", icon_only=True,emboss=False)
                            if value["hide"]:
                                continue
                            if "show_emitter" in value:
                                row = layout.row(align=True)
                                row.separator(factor=2)
                                row.separator(factor=2)
                                row.separator(factor=2)
                                row.separator(factor=2)
                                row.separator(factor=2)
                                row.label(icon="DOT")
                                row.label(text=bpy.app.translations.pgettext("Show Emitter"), icon="PARTICLES")
                                row.prop(value["show_emitter"], "show_instancer_for_viewport", icon="RESTRICT_VIEW_OFF" if obj.show_instancer_for_viewport else "RESTRICT_VIEW_ON", icon_only=True,emboss=False)
                                row.prop(value["show_emitter"], "show_instancer_for_render", icon="RESTRICT_RENDER_OFF" if obj.show_instancer_for_render else "RESTRICT_RENDER_ON", icon_only=True,emboss=False)
                            if "child_amount" in value:
                                row = layout.row(align=True)
                                row.separator(factor=2)
                                row.separator(factor=2)
                                row.separator(factor=2)
                                row.separator(factor=2)
                                row.separator(factor=2)
                                row.label(icon="DOT")
                                row.label(text=bpy.app.translations.pgettext("Child Amount"), icon="PARTICLES")
                                row.prop(value["child_amount"], "child_nbr")
                                row.prop(value["child_amount"], "rendered_child_count")
                            if "display_percentage" in value:
                                row = layout.row(align=True)
                                row.separator(factor=2)
                                row.separator(factor=2)
                                row.separator(factor=2)
                                row.separator(factor=2)
                                row.separator(factor=2)
                                row.label(icon="DOT")
                                row.label(text=bpy.app.translations.pgettext("Viewport Display Amount"), icon="PARTICLES")
                                row.prop(value["display_percentage"], "display_percentage")
                        for gpfx, value in mods["gpfxs"].items():
                            row = layout.row(align=True)
                            row.separator(factor=2)
                            row.separator(factor=2)
                            row.separator(factor=2)
                            row.separator(factor=2)
                            row.label(icon="DOT")
                            row.label(text=gpfx.name, icon="MODIFIER")
                            row.prop(gpfx, "show_viewport", icon_only=True,emboss=False)
                            row.prop(gpfx, "show_render", icon_only=True,emboss=False)
                        for fx, value in mods["fxs"].items():
                            row = layout.row(align=True)
                            row.separator(factor=2)
                            row.separator(factor=2)
                            row.separator(factor=2)
                            row.separator(factor=2)
                            row.label(icon="DOT")
                            row.label(text=fx.name, icon="SHADERFX")
                            row.prop(fx, "show_viewport", icon_only=True,emboss=False)
                            row.prop(fx, "show_render", icon_only=True,emboss=False)

class ATTENREN_PT_Menu_Settings(AttenRenPanel, bpy.types.Panel):
    bl_parent_id = "ATTENREN_PT_Menu"
    bl_label = bpy.app.translations.pgettext("Preferences")

    def draw(self, context):
        layout = self.layout
        layout.label(text=bpy.app.translations.pgettext("Check These Statues"))
        box = layout.box()
        box.prop(context.window_manager, "attenRen_settings_collVisibility")
        box.prop(context.window_manager, "attenRen_settings_objVisibility")
        box.prop(context.window_manager, "attenRen_settings_missingFiles")
        box.prop(context.window_manager, "attenRen_settings_renderRegion")
        box.prop(context.window_manager, "attenRen_settings_resolutionPercentage")
        box.prop(context.window_manager, "attenRen_settings_samples")
        box.prop(context.window_manager, "attenRen_settings_instance")
        box.prop(context.window_manager, "attenRen_settings_modifiers")
        row = box.row()
        row.alignment = "LEFT"
        row.prop(context.window_manager, "attenRen_settings_composite")
        row.label(text=bpy.app.translations.pgettext("(α Ver.)"))

        box.label(text=bpy.app.translations.pgettext("Particles"))
        row = box.row()
        row.separator(factor=1)
        row.prop(context.window_manager, "attenRen_settings_particleShowEmitter")
        row = box.row()
        row.separator(factor=1)
        row.prop(context.window_manager, "attenRen_settings_particleChildAmount")
        row = box.row()
        row.separator(factor=1)
        row.prop(context.window_manager, "attenRen_settings_particleDisplayPercentage")
        box.label(text=bpy.app.translations.pgettext("Grease Pencil"))
        row = box.row()
        row.separator(factor=1)
        row.prop(context.window_manager, "attenRen_settings_gpencilModifiers")
        row = box.row()
        row.separator(factor=1)
        row.prop(context.window_manager, "attenRen_settings_gpencilShaderEffects")
        layout.prop(context.window_manager, "attenRen_settings_autoCheck")