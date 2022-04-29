bl_info = {
    "name": "Attentive Rendering",
    "author": "Omine Taisei",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "3D Viewport",
    "description": "This Addon detects problems of your project and make your rendering more efficient",
    "warning": "",
    "support": "TESTING",
    "doc_url": "",
    "tracker_url": "",
    "category": "Interface"
}

if "bpy" in locals():
    import imp
    imp.reload(main)
    imp.reload(attenRenClass)
    imp.reload(translations)
else:
    from . import main
    from . import attenRenClass
    from . import translations

import bpy, os, json
from bpy.app.handlers import persistent
from bpy.props import (
    IntProperty,
    FloatProperty,
    # FloatVectorProperty,
    # EnumProperty,
    BoolProperty,
    StringProperty,
    PointerProperty,
)

def updateSettings(self, context):
    context.window_manager.attenRen.saveSettings()

def initProps():
    wm = bpy.types.WindowManager
    settings = []

    ### this should be in __init__ of attenRenClass but raise error, so done here 
    settingFilePath = os.path.join(os.path.dirname(__file__), "attenrenSettings.txt")
    if os.path.exists(settingFilePath):
        with open(settingFilePath, encoding='utf-8') as f:
            settings = json.load(f)
    ###

    wm.attenRen_settings_collVisibility = BoolProperty(
        name=bpy.app.translations.pgettext("Collections Visibiiity"),
        default=settings["attenRen_settings_collVisibility"]\
                if "attenRen_settings_collVisibility" in settings else True,
        update=updateSettings,
    )
    wm.attenRen_settings_objVisibility = BoolProperty(
        name=bpy.app.translations.pgettext("Objects Visibiiity"),
        default=settings["attenRen_settings_objVisibility"]\
                if "attenRen_settings_objVisibility" in settings else True,
        update=updateSettings,
    )
    wm.attenRen_settings_missingFiles = BoolProperty(
        name=bpy.app.translations.pgettext("Missing Files"),
        default=settings["attenRen_settings_missingFiles"]\
                if "attenRen_settings_missingFiles" in settings else True,
        update=updateSettings,
    )
    wm.attenRen_settings_renderRegion = BoolProperty(
        name=bpy.app.translations.pgettext("Render Region"),
        default=settings["attenRen_settings_renderRegion"]\
                if "attenRen_settings_renderRegion" in settings else True,
        update=updateSettings,
    )
    wm.attenRen_settings_resolutionPercentage = BoolProperty(
        name=bpy.app.translations.pgettext("Resolution %"),
        default=settings["attenRen_settings_resolutionPercentage"]\
                if "attenRen_settings_resolutionPercentage" in settings else True,
        update=updateSettings,
    )
    wm.attenRen_settings_samples = BoolProperty(
        name=bpy.app.translations.pgettext("Samples"),
        default=settings["attenRen_settings_samples"]\
                if "attenRen_settings_samples" in settings else True,
        update=updateSettings,
    )
    wm.attenRen_settings_instance = BoolProperty(
        name=bpy.app.translations.pgettext("Instancing"),
        default=settings["attenRen_settings_instance"]\
                if "attenRen_settings_instance" in settings else True,
        update=updateSettings,
    )
    wm.attenRen_settings_modifiers = BoolProperty(
        name=bpy.app.translations.pgettext("Modifiers"),
        default=settings["attenRen_settings_modifiers"]\
                if "attenRen_settings_modifiers" in settings else True,
        update=updateSettings,
    )
    wm.attenRen_settings_composite = BoolProperty(
        name=bpy.app.translations.pgettext("Composite"),
        default=settings["attenRen_settings_composite"]\
                if "attenRen_settings_composite" in settings else False,
        update=updateSettings,
    )
    wm.attenRen_settings_particleShowEmitter = BoolProperty(
        name=bpy.app.translations.pgettext("Show Emitter"),
        default=settings["attenRen_settings_particleShowEmitter"]\
                if "attenRen_settings_particleShowEmitter" in settings else True,
        update=updateSettings,
    )
    wm.attenRen_settings_particleChildAmount = BoolProperty(
        name=bpy.app.translations.pgettext("Child Amount"),
        default=settings["attenRen_settings_particleChildAmount"]\
                if "attenRen_settings_particleChildAmount" in settings else True,
        update=updateSettings,
    )
    wm.attenRen_settings_particleDisplayPercentage = BoolProperty(
        name=bpy.app.translations.pgettext("Viewport Display Amount"),
        default=settings["attenRen_settings_particleDisplayPercentage"]\
                if "attenRen_settings_particleDisplayPercentage" in settings else True,
        update=updateSettings,
    )
    wm.attenRen_settings_gpencilModifiers = BoolProperty(
        name=bpy.app.translations.pgettext("Modifiers"),
        default=settings["attenRen_settings_gpencilModifiers"]\
                if "attenRen_settings_gpencilModifiers" in settings else True,
        update=updateSettings,
    )
    wm.attenRen_settings_gpencilShaderEffects = BoolProperty(
        name=bpy.app.translations.pgettext("Effects"),
        default=settings["attenRen_settings_gpencilShaderEffects"]\
                if "attenRen_settings_gpencilShaderEffects" in settings else True,
        update=updateSettings,
    )
    wm.attenRen_settings_autoCheck = BoolProperty(
        name=bpy.app.translations.pgettext("Auto Check before Render"),
        description=bpy.app.translations.pgettext("Run AttentiveRendering Check Automatically before Rendering. (α Ver. Just Check and Refresh Addon Panel)"),
        default=settings["attenRen_settings_autoCheck"]\
                if "attenRen_settings_autoCheck" in settings else False,
        update=updateSettings,
    )
    wm.attenRen = attenRenClass.AttenRen()

def delProps():
    wm = bpy.types.WindowManager
    del wm.attenRen
    del wm.attenRen_settings_collVisibility
    del wm.attenRen_settings_objVisibility
    del wm.attenRen_settings_missingFiles
    del wm.attenRen_settings_renderRegion
    del wm.attenRen_settings_resolutionPercentage
    del wm.attenRen_settings_samples
    del wm.attenRen_settings_instance
    del wm.attenRen_settings_modifiers
    del wm.attenRen_settings_composite
    del wm.attenRen_settings_particleShowEmitter
    del wm.attenRen_settings_particleChildAmount
    del wm.attenRen_settings_particleDisplayPercentage
    del wm.attenRen_settings_gpencilModifiers
    del wm.attenRen_settings_gpencilShaderEffects
    del wm.attenRen_settings_autoCheck

# def topbarAppend(self, context):
#     layout = self.layout
#     layout.separator()
#     layout.prop(context.window_manager, "attenRen_settings_autoCheck")

# @persistent
# def autoCheckHandler(scene):
#     if scene.attenRen_settings_autoCheck:
#         bpy.ops.attenren.check()
#         # if scene.attenRen:
#         #     # self.report({'ERROR'}, bpy.app.translations.pgettext("Problems Detected"))
#         #     # bpy.context.window_manager.popup_menu(autoCheckPopUp, title="AttentiveRendering", icon='INFO')
#         #     bpy.context.window_manager.invoke_popup(autoCheckPopUp)
#         # else:
#         #     pass
#         #     # bpy.context.window_manager.popup_menu(autoCheckPopUp, title="AttentiveRendering", icon='INFO')
#         #     # self.report({'INFO'}, bpy.app.translations.pgettext("No Problems Detected"))

classes = [
    main.ATTENREN_OT_Check,
    main.ATTENREN_OT_SetObjHide,
    main.ATTENREN_OT_ClearRenderRegion,
    main.ATTENREN_OT_MatchVisibility,
    main.ATTENREN_OT_ToggleVisibilityInPanel,
    main.ATTENREN_PT_Menu,
    main.ATTENREN_PT_Menu_Settings,
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    initProps()
    # bpy.types.TOPBAR_MT_render.append(topbarAppend)
    bpy.app.translations.register(__name__, translations.translationDict)
    # bpy.app.handlers.render_pre.append(autoCheckHandler)

def unregister():
    bpy.app.translations.unregister(__name__)
    # bpy.types.TOPBAR_MT_render.remove(topbarAppend)
    delProps()
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()