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

def updatePrefs(self, context):
    context.window_manager.attenRen.savePrefs()

def initProps():
    wm = bpy.types.WindowManager
    prefs = []

    ### this should be in __init__ of attenRenClass but raise error, so done here 
    prefsFilePath = os.path.join(os.path.dirname(__file__), "attenrenPrefs.txt")
    if os.path.exists(prefsFilePath):
        with open(prefsFilePath, encoding='utf-8') as f:
            prefs = json.load(f)
    ###

    wm.attenRen_prefs_currentScene = BoolProperty(
        name="Current Scene Only",
        default=prefs["attenRen_prefs_currentScene"]\
                if "attenRen_prefs_currentScene" in prefs else False,
        update=updatePrefs,
    )
    wm.attenRen_prefs_currentViewLayer = BoolProperty(
        name="Current View Layer Only",
        default=prefs["attenRen_prefs_currentViewLayer"]\
                if "attenRen_prefs_currentViewLayer" in prefs else False,
        update=updatePrefs,
    )
    wm.attenRen_prefs_collVisibility = BoolProperty(
        name="Collections Visibiiity",
        default=prefs["attenRen_prefs_collVisibility"]\
                if "attenRen_prefs_collVisibility" in prefs else True,
        update=updatePrefs,
    )
    wm.attenRen_prefs_objVisibility = BoolProperty(
        name="Objects Visibiiity",
        default=prefs["attenRen_prefs_objVisibility"]\
                if "attenRen_prefs_objVisibility" in prefs else True,
        update=updatePrefs,
    )
    wm.attenRen_prefs_missingFiles = BoolProperty(
        name="Missing Files",
        default=prefs["attenRen_prefs_missingFiles"]\
                if "attenRen_prefs_missingFiles" in prefs else True,
        update=updatePrefs,
    )
    wm.attenRen_prefs_renderRegion = BoolProperty(
        name="Render Region",
        default=prefs["attenRen_prefs_renderRegion"]\
                if "attenRen_prefs_renderRegion" in prefs else True,
        update=updatePrefs,
    )
    wm.attenRen_prefs_resolutionPercentage = BoolProperty(
        name="Resolution %",
        default=prefs["attenRen_prefs_resolutionPercentage"]\
                if "attenRen_prefs_resolutionPercentage" in prefs else True,
        update=updatePrefs,
    )
    wm.attenRen_prefs_samples = BoolProperty(
        name="Samples",
        default=prefs["attenRen_prefs_samples"]\
                if "attenRen_prefs_samples" in prefs else True,
        update=updatePrefs,
    )
    wm.attenRen_prefs_instance = BoolProperty(
        name="Instancing",
        default=prefs["attenRen_prefs_instance"]\
                if "attenRen_prefs_instance" in prefs else True,
        update=updatePrefs,
    )
    wm.attenRen_prefs_modifiers = BoolProperty(
        name="Modifiers",
        default=prefs["attenRen_prefs_modifiers"]\
                if "attenRen_prefs_modifiers" in prefs else True,
        update=updatePrefs,
    )
    wm.attenRen_prefs_composite = BoolProperty(
        name="Composite",
        default=prefs["attenRen_prefs_composite"]\
                if "attenRen_prefs_composite" in prefs else False,
        update=updatePrefs,
    )
    wm.attenRen_prefs_particleShowEmitter = BoolProperty(
        name="Show Emitter",
        default=prefs["attenRen_prefs_particleShowEmitter"]\
                if "attenRen_prefs_particleShowEmitter" in prefs else True,
        update=updatePrefs,
    )
    wm.attenRen_prefs_particleChildAmount = BoolProperty(
        name="Child Amount",
        default=prefs["attenRen_prefs_particleChildAmount"]\
                if "attenRen_prefs_particleChildAmount" in prefs else True,
        update=updatePrefs,
    )
    wm.attenRen_prefs_particleDisplayPercentage = BoolProperty(
        name="Viewport Display Amount",
        default=prefs["attenRen_prefs_particleDisplayPercentage"]\
                if "attenRen_prefs_particleDisplayPercentage" in prefs else True,
        update=updatePrefs,
    )
    wm.attenRen_prefs_gpencilModifiers = BoolProperty(
        name="Modifiers",
        default=prefs["attenRen_prefs_gpencilModifiers"]\
                if "attenRen_prefs_gpencilModifiers" in prefs else True,
        update=updatePrefs,
    )
    wm.attenRen_prefs_gpencilShaderEffects = BoolProperty(
        name="Effects",
        default=prefs["attenRen_prefs_gpencilShaderEffects"]\
                if "attenRen_prefs_gpencilShaderEffects" in prefs else True,
        update=updatePrefs,
    )
    wm.attenRen_prefs_autoCheck = BoolProperty(
        name="Auto Check before Render",
        description=bpy.app.translations.pgettext_iface("Run AttentiveRendering Check Automatically before Rendering. (α Ver. Just Check and Refresh Addon Panel)"),
        default=prefs["attenRen_prefs_autoCheck"]\
                if "attenRen_prefs_autoCheck" in prefs else False,
        update=updatePrefs,
    )
    wm.attenRen = attenRenClass.AttenRen()

def delProps():
    wm = bpy.types.WindowManager
    del wm.attenRen
    del wm.attenRen_prefs_currentScene
    del wm.attenRen_prefs_currentViewLayer
    del wm.attenRen_prefs_collVisibility
    del wm.attenRen_prefs_objVisibility
    del wm.attenRen_prefs_missingFiles
    del wm.attenRen_prefs_renderRegion
    del wm.attenRen_prefs_resolutionPercentage
    del wm.attenRen_prefs_samples
    del wm.attenRen_prefs_instance
    del wm.attenRen_prefs_modifiers
    del wm.attenRen_prefs_composite
    del wm.attenRen_prefs_particleShowEmitter
    del wm.attenRen_prefs_particleChildAmount
    del wm.attenRen_prefs_particleDisplayPercentage
    del wm.attenRen_prefs_gpencilModifiers
    del wm.attenRen_prefs_gpencilShaderEffects
    del wm.attenRen_prefs_autoCheck

# def topbarAppend(self, context):
#     layout = self.layout
#     layout.separator()
#     layout.prop(context.window_manager, "attenRen_prefs_autoCheck")

# @persistent
# def autoCheckHandler(scene):
#     if scene.attenRen_prefs_autoCheck:
#         bpy.ops.attenren.check()
#         # if scene.attenRen:
#         #     # self.report({'ERROR'}, bpy.app.translations.pgettext_iface("Problems Detected"))
#         #     # bpy.context.window_manager.popup_menu(autoCheckPopUp, title="AttentiveRendering", icon='INFO')
#         #     bpy.context.window_manager.invoke_popup(autoCheckPopUp)
#         # else:
#         #     pass
#         #     # bpy.context.window_manager.popup_menu(autoCheckPopUp, title="AttentiveRendering", icon='INFO')
#         #     # self.report({'INFO'}, bpy.app.translations.pgettext_iface("No Problems Detected"))
@persistent
def resetDataHandler(scene):
    bpy.context.window_manager.attenRen.checkedItems.clear()
    bpy.context.window_manager.attenRen.missingFiles.clear()
    bpy.context.window_manager.attenRen.notCheckedYet = True

classes = [
    main.ATTENREN_OT_Check,
    main.ATTENREN_OT_SetObjHide,
    main.ATTENREN_OT_ClearRenderRegion,
    main.ATTENREN_OT_MatchVisibility,
    main.ATTENREN_OT_ToggleVisibilityInPanel,
    main.ATTENREN_PT_Menu,
    main.ATTENREN_PT_Menu_Prefs,
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    initProps()
    # bpy.types.TOPBAR_MT_render.append(topbarAppend)
    bpy.app.translations.register(__name__, translations.translationDict)
    bpy.app.handlers.load_pre.append(resetDataHandler)
    # bpy.app.handlers.render_pre.append(autoCheckHandler)

def unregister():
    bpy.app.translations.unregister(__name__)
    # bpy.types.TOPBAR_MT_render.remove(topbarAppend)
    delProps()
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()