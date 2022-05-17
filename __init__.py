bl_info = {
    "name": "FinalCheck",
    "author": "Taisei Omine",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "3D Viewport",
    "description": "This addon detects problems of your project and make your rendering more efficient",
    "warning": "",
    "support": "COMMUNITY",
    "doc_url": "https://github.com/omine-me/FinalCheck",
    "tracker_url": "https://github.com/omine-me/FinalCheck/issues",
    "category": "Interface"
}

if "bpy" in locals():
    import imp
    imp.reload(main)
    imp.reload(finalCheckClass)
    imp.reload(translations)
else:
    from . import main
    from . import finalCheckClass
    from . import translations

import bpy, os, json
from bpy.app.handlers import persistent
from bpy.props import (
    BoolProperty,
)

def updatePrefs(self, context):
    context.window_manager.finalCheck.savePrefs()

def initProps():
    wm = bpy.types.WindowManager
    prefs = []
    trans=bpy.app.translations.pgettext_tip

    ### this may be in __init__ of finalCheckClass but raise error, so done here 
    prefsFilePath = os.path.join(os.path.dirname(__file__), "FinalCheckPrefs.txt")
    if os.path.exists(prefsFilePath):
        with open(prefsFilePath, encoding='utf-8') as f:
            prefs = json.load(f)
    ###

    wm.finalCheck_prefs_currentScene = BoolProperty(
        name="Current Scene Only",
        default=prefs["finalCheck_prefs_currentScene"]\
                if "finalCheck_prefs_currentScene" in prefs else False,
        description=trans("Check Current Scene Only"),
        update=updatePrefs,
    )
    wm.finalCheck_prefs_currentViewLayer = BoolProperty(
        name="Current View Layer Only",
        default=prefs["finalCheck_prefs_currentViewLayer"]\
                if "finalCheck_prefs_currentViewLayer" in prefs else False,
        description=trans("Check Current View Layer Only (When Current Scene Only Is True)"),
        update=updatePrefs,
    )
    wm.finalCheck_prefs_collVisibility = BoolProperty(
        name="Collections Visibiiity",
        default=prefs["finalCheck_prefs_collVisibility"]\
                if "finalCheck_prefs_collVisibility" in prefs else True,
        description=trans("Does Visibility of Collections in Viewports and Renders Differ?"),
        update=updatePrefs,
    )
    wm.finalCheck_prefs_objVisibility = BoolProperty(
        name="Objects Visibiiity",
        default=prefs["finalCheck_prefs_objVisibility"]\
                if "finalCheck_prefs_objVisibility" in prefs else True,
        description=trans("Does Visibility of Objects in Viewports and Renders Differ?"),
        update=updatePrefs,
    )
    wm.finalCheck_prefs_missingFiles = BoolProperty(
        name="Missing Files",
        default=prefs["finalCheck_prefs_missingFiles"]\
                if "finalCheck_prefs_missingFiles" in prefs else True,
        description=trans("Is an Image Path Broken?"),
        update=updatePrefs,
    )
    wm.finalCheck_prefs_renderRegion = BoolProperty(
        name="Render Region",
        default=prefs["finalCheck_prefs_renderRegion"]\
                if "finalCheck_prefs_renderRegion" in prefs else True,
        description=trans("Is Render Region Set and the Area Reduced?"),
        update=updatePrefs,
    )
    wm.finalCheck_prefs_resolutionPercentage = BoolProperty(
        name="Resolution %",
        default=prefs["finalCheck_prefs_resolutionPercentage"]\
                if "finalCheck_prefs_resolutionPercentage" in prefs else True,
        description=trans("Is Resolution% Under 100%?"),
        update=updatePrefs,
    )
    wm.finalCheck_prefs_samples = BoolProperty(
        name="Samples",
        default=prefs["finalCheck_prefs_samples"]\
                if "finalCheck_prefs_samples" in prefs else True,
        description=trans("Is Render Samples Under Preview Samples?"),
        update=updatePrefs,
    )
    wm.finalCheck_prefs_instance = BoolProperty(
        name="Instancing",
        default=prefs["finalCheck_prefs_instance"]\
                if "finalCheck_prefs_instance" in prefs else True,
        description=trans("Does Visibility of Instancer in Viewports and Renders Differ?"),
        update=updatePrefs,
    )
    wm.finalCheck_prefs_modifiers = BoolProperty(
        name="Modifiers",
        default=prefs["finalCheck_prefs_modifiers"]\
                if "finalCheck_prefs_modifiers" in prefs else True,
        description=trans("Does Visibility of Modifiers in Viewports and Renders Differ?"),
        update=updatePrefs,
    )
    wm.finalCheck_prefs_composite = BoolProperty(
        name="Composite",
        default=prefs["finalCheck_prefs_composite"]\
                if "finalCheck_prefs_composite" in prefs else False,
        description=trans("Do Inputs of Viewer Node and Composite Node Differ? This I Currently Incomplete Due to Limitations of The Blender Python API"),
        update=updatePrefs,
    )
    wm.finalCheck_prefs_particleShowEmitter = BoolProperty(
        name="Show Emitter",
        default=prefs["finalCheck_prefs_particleShowEmitter"]\
                if "finalCheck_prefs_particleShowEmitter" in prefs else True,
        description=trans("Does Visibility of Particle Emitter in Viewports and Renders Differ?"),
        update=updatePrefs,
    )
    wm.finalCheck_prefs_particleChildAmount = BoolProperty(
        name="Child Amount",
        default=prefs["finalCheck_prefs_particleChildAmount"]\
                if "finalCheck_prefs_particleChildAmount" in prefs else True,
        description=trans("Does Child Amount of Particles in Viewports and Renders Differ?"),
        update=updatePrefs,
    )
    wm.finalCheck_prefs_particleDisplayPercentage = BoolProperty(
        name="Viewport Display Amount",
        default=prefs["finalCheck_prefs_particleDisplayPercentage"]\
                if "finalCheck_prefs_particleDisplayPercentage" in prefs else True,
        description=trans("Is Amount of Particles in Viewports Under 100%?"),
        update=updatePrefs,
    )
    wm.finalCheck_prefs_gpencilModifiers = BoolProperty(
        name="Modifiers",
        default=prefs["finalCheck_prefs_gpencilModifiers"]\
                if "finalCheck_prefs_gpencilModifiers" in prefs else True,
        description=trans("Does Visibility of Modifiers in Viewports and Renders Differ?"),
        update=updatePrefs,
    )
    wm.finalCheck_prefs_gpencilShaderEffects = BoolProperty(
        name="Effects",
        default=prefs["finalCheck_prefs_gpencilShaderEffects"]\
                if "finalCheck_prefs_gpencilShaderEffects" in prefs else True,
        description=trans("Does Visibility of Effects in Viewports and Renders Differ?"),
        update=updatePrefs,
    )
    wm.finalCheck = finalCheckClass.FinalCheck()

def delProps():
    wm = bpy.types.WindowManager
    del wm.finalCheck
    del wm.finalCheck_prefs_currentScene
    del wm.finalCheck_prefs_currentViewLayer
    del wm.finalCheck_prefs_collVisibility
    del wm.finalCheck_prefs_objVisibility
    del wm.finalCheck_prefs_missingFiles
    del wm.finalCheck_prefs_renderRegion
    del wm.finalCheck_prefs_resolutionPercentage
    del wm.finalCheck_prefs_samples
    del wm.finalCheck_prefs_instance
    del wm.finalCheck_prefs_modifiers
    del wm.finalCheck_prefs_composite
    del wm.finalCheck_prefs_particleShowEmitter
    del wm.finalCheck_prefs_particleChildAmount
    del wm.finalCheck_prefs_particleDisplayPercentage
    del wm.finalCheck_prefs_gpencilModifiers
    del wm.finalCheck_prefs_gpencilShaderEffects

@persistent
def resetDataHandler(scene):
    wm = bpy.context.window_manager
    wm.finalCheck.checkedItems.clear()
    wm.finalCheck.missingFiles.clear()
    wm.finalCheck.notCheckedYet = True
    prefsFilePath = os.path.join(os.path.dirname(__file__), "FinalCheckPrefs.txt")
    if os.path.exists(prefsFilePath):
        with open(prefsFilePath, encoding='utf-8') as f:
            prefs = json.load(f)
        try:
            wm.finalCheck_prefs_currentScene = prefs["finalCheck_prefs_currentScene"]
        except: pass
        try:
            wm.finalCheck_prefs_currentViewLayer = prefs["finalCheck_prefs_currentViewLayer"]
        except: pass
        try:
            wm.finalCheck_prefs_collVisibility = prefs["finalCheck_prefs_collVisibility"]
        except: pass
        try:
            wm.finalCheck_prefs_objVisibility = prefs["finalCheck_prefs_objVisibility"]
        except: pass
        try:
            wm.finalCheck_prefs_missingFiles = prefs["finalCheck_prefs_missingFiles"]
        except: pass
        try:
            wm.finalCheck_prefs_renderRegion = prefs["finalCheck_prefs_renderRegion"]
        except: pass
        try:
            wm.finalCheck_prefs_resolutionPercentage = prefs["finalCheck_prefs_resolutionPercentage"]
        except: pass
        try:
            wm.finalCheck_prefs_samples = prefs["finalCheck_prefs_samples"]
        except: pass
        try:
            wm.finalCheck_prefs_instance = prefs["finalCheck_prefs_instance"]
        except: pass
        try:
            wm.finalCheck_prefs_modifiers = prefs["finalCheck_prefs_modifiers"]
        except: pass
        try:
            wm.finalCheck_prefs_composite = prefs["finalCheck_prefs_composite"]
        except: pass
        try:
            wm.finalCheck_prefs_particleShowEmitter = prefs["finalCheck_prefs_particleShowEmitter"]
        except: pass
        try:
            wm.finalCheck_prefs_particleChildAmount = prefs["finalCheck_prefs_particleChildAmount"]
        except: pass
        try:
            wm.finalCheck_prefs_particleDisplayPercentage = prefs["finalCheck_prefs_particleDisplayPercentage"]
        except: pass
        try:
            wm.finalCheck_prefs_gpencilModifiers = prefs["finalCheck_prefs_gpencilModifiers"]
        except: pass
        try:
            wm.finalCheck_prefs_gpencilShaderEffects = prefs["finalCheck_prefs_gpencilShaderEffects"]
        except: pass

classes = [
    main.FINALCHECK_OT_Check,
    main.FINALCHECK_OT_SetObjHide,
    main.FINALCHECK_OT_ClearRenderRegion,
    main.FINALCHECK_OT_ToggleVisibilityInPanel,
    main.FINALCHECK_PT_Menu,
    main.FINALCHECK_PT_Menu_Prefs,
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    initProps()
    bpy.app.translations.register(__name__, translations.translationDict)
    bpy.app.handlers.load_post.append(resetDataHandler) ### not load_pre because setting prefs doesn't work well.

def unregister():
    bpy.app.translations.unregister(__name__)
    delProps()
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()