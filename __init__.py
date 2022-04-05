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

import bpy
from bpy.props import (
    IntProperty,
    FloatProperty,
    # FloatVectorProperty,
    # EnumProperty,
    BoolProperty,
    StringProperty,
    PointerProperty,
)

def initProps():
    scene = bpy.types.Scene
    scene.attenRen = attenRenClass.AttenRen()
    # scene.attenRenActiveObj = PointerProperty(
    #     # type=bpy.types.PropertyGroup,
    #     type=bpy.types.Object,
    #     name="obj",
    #     options={"HIDDEN"},
    # )
    scene.attenRen_settings_collVisibility = BoolProperty(
        name=bpy.app.translations.pgettext("Collections Visibiiity"),
        default=True,
        # update=update.setIsCtrl
    )
    scene.attenRen_settings_objVisibility = BoolProperty(
        name=bpy.app.translations.pgettext("Objects Visibiiity"),
        default=True,
        # update=update.setIsCtrl
    )
    scene.attenRen_settings_missingFiles = BoolProperty(
        name=bpy.app.translations.pgettext("Missing Files"),
        default=True,
        # update=update.setIsCtrl
    )
    scene.attenRen_settings_renderRegion = BoolProperty(
        name=bpy.app.translations.pgettext("Render Region"),
        default=True,
        # update=update.setIsCtrl
    )
    scene.attenRen_settings_resolutionPercentage = BoolProperty(
        name=bpy.app.translations.pgettext("Resolution %"),
        default=True,
        # update=update.setIsCtrl
    )
    scene.attenRen_settings_samples = BoolProperty(
        name=bpy.app.translations.pgettext("Samples"),
        default=True,
        # update=update.setIsCtrl
    )
    scene.attenRen_settings_instance = BoolProperty(
        name=bpy.app.translations.pgettext("Instancing"),
        default=True,
        # update=update.setIsCtrl
    )
    scene.attenRen_settings_modifiers = BoolProperty(
        name=bpy.app.translations.pgettext("Modifiers"),
        default=True,
        # update=update.setIsCtrl
    )
    scene.attenRen_settings_composite = BoolProperty(
        name=bpy.app.translations.pgettext("Composite"),
        default=True,
        # update=update.setIsCtrl
    )
    scene.attenRen_settings_particleShowEmitter = BoolProperty(
        name=bpy.app.translations.pgettext("Show Emitter"),
        default=True,
        # update=update.setIsCtrl
    )
    scene.attenRen_settings_particleChildAmount = BoolProperty(
        name=bpy.app.translations.pgettext("Child Amount"),
        default=True,
        # update=update.setIsCtrl
    )
    scene.attenRen_settings_particleDisplayPercentage = BoolProperty(
        name=bpy.app.translations.pgettext("Viewport Display Amount"),
        default=True,
        # update=update.setIsCtrl
    )
    scene.attenRen_settings_gpencilModifiers = BoolProperty(
        name=bpy.app.translations.pgettext("Modifiers"),
        default=True,
        # update=update.setIsCtrl
    )
    scene.attenRen_settings_gpencilShaderEffects = BoolProperty(
        name=bpy.app.translations.pgettext("Effects"),
        default=True,
        # update=update.setIsCtrl
    )
    # scene.autoHairRoundness = FloatProperty(
    #     name="Roundness",
    #     description="Children's roundness",
    #     default=0.0,
    #     min=0.0,
    #     max=1.0,
    #     # update=io.load("C:/opencv/VSproject/OpenCV/x64/Debug/out/00100/00100Ori_gt.mat")
    # )
    # scene.defaultHairNum = IntProperty(
    #     name="defaultHairNum",
    #     description="",
    #     default=const.DEFAULTHAIRNUM
    # )
    # scene.autoHairBraidInfoTxtPath = StringProperty(
    #     name="Braid Info .Txt Path",
    # )
    # scene.autoHairBangMatPath = StringProperty(
    #     name="Bang .Mat Path",
    #     description="Mat Path for Bang Synthesis",
    # )

def delProps():
    scene = bpy.types.Scene
    del scene.attenRen
    del scene.attenRen_settings_collVisibility
    del scene.attenRen_settings_objVisibility
    del scene.attenRen_settings_missingFiles
    del scene.attenRen_settings_renderRegion
    del scene.attenRen_settings_resolutionPercentage
    del scene.attenRen_settings_samples
    del scene.attenRen_settings_instance
    del scene.attenRen_settings_modifiers
    del scene.attenRen_settings_composite
    del scene.attenRen_settings_particleShowEmitter
    del scene.attenRen_settings_particleChildAmount
    del scene.attenRen_settings_particleDisplayPercentage
    del scene.attenRen_settings_gpencilModifiers
    del scene.attenRen_settings_gpencilShaderEffects

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
    bpy.app.translations.register(__name__, translations.translationDict)


def unregister():
    bpy.app.translations.unregister(__name__)
    delProps()
    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()