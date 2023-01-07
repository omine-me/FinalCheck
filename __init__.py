bl_info = {
    "name": "FinalCheck",
    "author": "Taisei Omine",
    "version": (0, 2, 1),
    "blender": (2, 90, 0),
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
from bpy.app.translations import (
    pgettext_iface as iface_,
    pgettext_tip as tip_,
)

def updatePrefs(self, context):
    context.window_manager.finalCheck.savePrefs()

def render_menu(self, context):
    layout = self.layout
    layout.operator("finalcheck.render", text=iface_("Check and Render Image"),
                        icon='RENDER_STILL').use_viewport = True
    props = layout.operator("finalcheck.render", 
                            text=iface_("Check and Render Animation"), icon='RENDER_ANIMATION')
    props.animation = True
    props.use_viewport = True
    layout.separator()

def toggleAutoCheck_disable(context):
    bpy.types.TOPBAR_MT_render.remove(render_menu)
    # remove shortcuts
    inherited_render_idname = bpy.ops.render.render.idname_py()
    kc = context.window_manager.keyconfigs.user
    for km in ['Screen', 'Screen Editing']:
        if km not in kc.keymaps:
            continue
        km = kc.keymaps[km]
        for km_item in km.keymap_items:
            if km_item.idname == inherited_render_idname:
                correspondent_keymap_found = False
                for _km_item in km.keymap_items:
                    if (_km_item.idname == bpy.types.FINALCHECK_OT_render.bl_idname and
                        _km_item.type == km_item.type and _km_item.value == km_item.value and
                        _km_item.any == km_item.any and _km_item.shift == km_item.shift and
                        _km_item.ctrl == km_item.ctrl and _km_item.alt == km_item.alt and
                        _km_item.oskey == km_item.oskey and _km_item.key_modifier == km_item.key_modifier):
                            km_item.active = _km_item.active
                            km.keymap_items.remove(_km_item)
                            correspondent_keymap_found = True
                            break
                # If correspond inherited render keymap can't be found,
                # make it enabled without considering the state before enabling AutoCheck.
                if not correspondent_keymap_found:
                    km_item.active = True

        # do second removal because there may be a remaining keymap
        # if correspondent_keymap_found was False
        for _km_item in km.keymap_items:
            if _km_item.idname == bpy.types.FINALCHECK_OT_render.bl_idname:
                km.keymap_items.remove(_km_item)

def toggleAutoCheck(self=None, context=None):
    context = bpy.context
    if context.window_manager.finalCheck_prefs_autoCheck:
        bpy.types.TOPBAR_MT_render.prepend(render_menu)
        # change shortcuts
        inherited_render_idname = bpy.ops.render.render.idname_py()
        kc = context.window_manager.keyconfigs.user
        for km in ['Screen', 'Screen Editing']: # Screen Editing is used in Industry_Compatible keymap
            if km not in kc.keymaps:
                continue
            km = kc.keymaps[km]
            for km_item in km.keymap_items:
                if km_item.idname == inherited_render_idname:
                    new_km = km.keymap_items.new(bpy.types.FINALCHECK_OT_render.bl_idname,
                                km_item.type, km_item.value,
                                any=km_item.any, shift=km_item.shift, ctrl=km_item.ctrl,
                                alt=km_item.alt, oskey=km_item.oskey, key_modifier=km_item.key_modifier)
                    for prop_name, prop_val in km_item.properties.items():
                        setattr(new_km.properties, prop_name, prop_val)
                    if not km_item.active:
                        new_km.active = False
                    km_item.active = False
    else:
        toggleAutoCheck_disable(context)

    if self:
        updatePrefs(self, context)

def initProps():
    wm = bpy.types.WindowManager
    prefs = []

    ### this may be in __init__ of finalCheckClass but raise error, so done here 
    prefsFilePath = os.path.join(os.path.dirname(__file__), "FinalCheckPrefs.txt")
    if os.path.exists(prefsFilePath):
        with open(prefsFilePath, encoding='utf-8') as f:
            prefs = json.load(f)
    ###

    wm.finalCheck_prefs_autoCheck = BoolProperty(
        name="Auto Check",
        default=prefs["finalCheck_prefs_autoCheck"]\
                if "finalCheck_prefs_autoCheck" in prefs else False,
        description=tip_("Check automatically before render"),
        update=toggleAutoCheck,
    )
    wm.finalCheck_prefs_currentScene = BoolProperty(
        name="Current Scene Only",
        default=prefs["finalCheck_prefs_currentScene"]\
                if "finalCheck_prefs_currentScene" in prefs else False,
        description=tip_("Check current scene only"),
        update=updatePrefs,
    )
    wm.finalCheck_prefs_currentViewLayer = BoolProperty(
        name="Current View Layer Only",
        default=prefs["finalCheck_prefs_currentViewLayer"]\
                if "finalCheck_prefs_currentViewLayer" in prefs else False,
        description=tip_("Check current view layer only (When Current Scene Only is enabled)"),
        update=updatePrefs,
    )
    wm.finalCheck_prefs_collVisibility = BoolProperty(
        name="Collections Visibiiity",
        default=prefs["finalCheck_prefs_collVisibility"]\
                if "finalCheck_prefs_collVisibility" in prefs else True,
        description=tip_("Compare visibility of collections in viewport and render"),
        update=updatePrefs,
    )
    wm.finalCheck_prefs_objVisibility = BoolProperty(
        name="Objects Visibiiity",
        default=prefs["finalCheck_prefs_objVisibility"]\
                if "finalCheck_prefs_objVisibility" in prefs else True,
        description=tip_("Compare visibility of objects in viewport and render"),
        update=updatePrefs,
    )
    wm.finalCheck_prefs_missingFiles = BoolProperty(
        name="Missing Files",
        default=prefs["finalCheck_prefs_missingFiles"]\
                if "finalCheck_prefs_missingFiles" in prefs else True,
        description=tip_("Check image path validity"),
        update=updatePrefs,
    )
    wm.finalCheck_prefs_renderRegion = BoolProperty(
        name="Render Region",
        default=prefs["finalCheck_prefs_renderRegion"]\
                if "finalCheck_prefs_renderRegion" in prefs else True,
        description=tip_("Check if Render Region is not set"),
        update=updatePrefs,
    )
    wm.finalCheck_prefs_resolutionPercentage = BoolProperty(
        name="Resolution %",
        default=prefs["finalCheck_prefs_resolutionPercentage"]\
                if "finalCheck_prefs_resolutionPercentage" in prefs else True,
        description=tip_("Check if Resolution% is greater than or equal to 100%"),
        update=updatePrefs,
    )
    wm.finalCheck_prefs_samples = BoolProperty(
        name="Samples",
        default=prefs["finalCheck_prefs_samples"]\
                if "finalCheck_prefs_samples" in prefs else True,
        description=tip_("Check if render samples are greater than or equal to preview samples"),
        update=updatePrefs,
    )
    wm.finalCheck_prefs_instance = BoolProperty(
        name="Instancing",
        default=prefs["finalCheck_prefs_instance"]\
                if "finalCheck_prefs_instance" in prefs else True,
        description=tip_("Compare visibility of instancer in viewport and render"),
        update=updatePrefs,
    )
    wm.finalCheck_prefs_modifiers = BoolProperty(
        name="Modifiers",
        default=prefs["finalCheck_prefs_modifiers"]\
                if "finalCheck_prefs_modifiers" in prefs else True,
        description=tip_("Compare visibility of modifiers in viewport and render"),
        update=updatePrefs,
    )
    wm.finalCheck_prefs_composite = BoolProperty(
        name="Composite",
        default=prefs["finalCheck_prefs_composite"]\
                if "finalCheck_prefs_composite" in prefs else False,
        description=tip_("Check if inputs of Viewer node and Composite node are the same. This is currently incomplete due to limitations of Blender Python API"),
        update=updatePrefs,
    )
    wm.finalCheck_prefs_particleShowEmitter = BoolProperty(
        name="Show Emitter",
        default=prefs["finalCheck_prefs_particleShowEmitter"]\
                if "finalCheck_prefs_particleShowEmitter" in prefs else True,
        description=tip_("Compare visibility of particle emitter in viewport and render"),
        update=updatePrefs,
    )
    wm.finalCheck_prefs_particleChildAmount = BoolProperty(
        name="Child Amount",
        default=prefs["finalCheck_prefs_particleChildAmount"]\
                if "finalCheck_prefs_particleChildAmount" in prefs else True,
        description=tip_("Check if child amount of particles in viewport and render are the same"),
        update=updatePrefs,
    )
    wm.finalCheck_prefs_particleDisplayPercentage = BoolProperty(
        name="Viewport Display Amount",
        default=prefs["finalCheck_prefs_particleDisplayPercentage"]\
                if "finalCheck_prefs_particleDisplayPercentage" in prefs else False,
        description=tip_("Check if amount of particles in viewport is 100%"),
        update=updatePrefs,
    )
    wm.finalCheck_prefs_gpencilModifiers = BoolProperty(
        name="Modifiers",
        default=prefs["finalCheck_prefs_gpencilModifiers"]\
                if "finalCheck_prefs_gpencilModifiers" in prefs else True,
        description=tip_("Compare visibility of modifiers in viewport and render"),
        update=updatePrefs,
    )
    wm.finalCheck_prefs_gpencilShaderEffects = BoolProperty(
        name="Effects",
        default=prefs["finalCheck_prefs_gpencilShaderEffects"]\
                if "finalCheck_prefs_gpencilShaderEffects" in prefs else True,
        description=tip_("Compare visibility of effects in viewport and render"),
        update=updatePrefs,
    )
    wm.finalCheck = finalCheckClass.FinalCheck()

def delProps():
    wm = bpy.types.WindowManager
    del wm.finalCheck
    del wm.finalCheck_prefs_autoCheck
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
    initProps()

classes = [
    main.FINALCHECK_OT_Check,
    main.FINALCHECK_OT_SetObjHide,
    main.FINALCHECK_OT_ClearRenderRegion,
    main.FINALCHECK_OT_ToggleVisibilityInPanel,
    main.FINALCHECK_OT_SelectObject,
    main.FINALCHECK_OT_Render,
    main.FINALCHECK_PT_Menu,
    main.FINALCHECK_PT_Menu_Prefs,
]

def del_lazy_load(self=None, context=None):
    bpy.app.handlers.load_post.remove(lazy_load)

# lazy_load_done is needed when open blender with specific file
# because multiple bpy.app.handlers.load_post triggers.
lazy_load_done = False
# need persistent but one time is enough. So delete this finally.
@persistent
def lazy_load(scene):
    global lazy_load_done
    if not lazy_load_done:
        lazy_load_done = True
        bpy.app.timers.register(toggleAutoCheck, first_interval=.3, persistent=True)
        bpy.app.timers.register(del_lazy_load, first_interval=.5, persistent=True)

def register():
    for c in classes:
        bpy.utils.register_class(c)
    initProps()
    bpy.app.translations.register(__name__, translations.translationDict)
    bpy.app.handlers.load_post.append(resetDataHandler)
    # check wheather it is starting up or just enabling addon
    if len(bpy.context.window_manager.keyconfigs.user.keymaps) \
        < len(bpy.context.window_manager.keyconfigs.active.keymaps):
        # toggleAutoCheck has to be done after loading all because user keymap isn't loaded at register.
        bpy.app.handlers.load_post.append(lazy_load)
    else:
        toggleAutoCheck()

def unregister():
    if bpy.context.window_manager.finalCheck_prefs_autoCheck:
        toggleAutoCheck_disable(bpy.context)

    bpy.app.translations.unregister(__name__)
    delProps()
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
