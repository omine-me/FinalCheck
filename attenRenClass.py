import bpy, os, json

class AttenRen:
    def __init__(self):
        #VISIB_MODE = "EYE" #"DISPLAY", "BOTH"
        #VISIB_MODE = "DISPLAY"
        self.VISIB_MODE = "BOTH"
        self.missingFiles = {}
        self.checkedItems = {}
        """ 
        {   
            scene1: {
                hide: True,?
                view_layers:{
                    view_layer1:{
                        hide: True,?
                        colls:{
                            Scene's Master Coll: {...}, #Scene's Master Coll must be first because of the argorhythm in ATTENREN_PT_Menu
                            coll1:{
                                hide: True,
                                objs:{
                                    obj1:{
                                        hide: True,
                                        mods{
                                            modifier1{

                                            },
                                            ...,
                                        },
                                    }, 
                                    ...,
                                },
                            },
                            ...,
                        },
                    },
                    ...,
                },
            },
            ...,
        }
        """
        # settingFilePath = os.path.join(os.path.dirname(__file__), "attenrenSettings.txt")
        # if os.path.exists(settingFilePath):
        #     with open(settingFilePath, encoding='utf-8') as f:
        #         scene = bpy.context.scene
        #         settings = json.load(f)
        #         for key, val in settings.items():
        #             setattr(scene, key, val) 

    def clearRenderRegion(self, renderSettings):
        renderSettings.border_max_x = 1.
        renderSettings.border_max_y = 1.
        renderSettings.border_min_x = 0.
        renderSettings.border_min_y = 0.
        renderSettings.use_border = False

    def objectCheck(self, vl, objsDict, obj):
        wm = bpy.context.window_manager
        addToObjsDict = False
        objDict = {"hide": False}
        if wm.attenRen_settings_objVisibility:
            if self.VISIB_MODE == "EYE":
                if not obj.hide_get(view_layer=vl) == obj.hide_render:
                    addToObjsDict = True
                    objDict = {"hide": False}
            elif self.VISIB_MODE == "DISPLAY":
                if not obj.hide_viewport == obj.hide_render:
                    addToObjsDict = True
                    objDict = {"hide": False}
            else:
                if (((obj.hide_get(view_layer=vl) != obj.hide_viewport) and obj.hide_render == False) or 
                    ((obj.hide_get(view_layer=vl) == obj.hide_viewport == False) and obj.hide_render == True) or
                    ((obj.hide_get(view_layer=vl) == obj.hide_viewport == True) and obj.hide_render == False)):
                    addToObjsDict = True
                    objDict = {"hide": False}
        modifiersDict = {}
        for mod in obj.modifiers:
            if wm.attenRen_settings_modifiers and mod.show_render != mod.show_viewport:
                addToObjsDict = True
                modifiersDict[mod] = {"hide": False}
            if mod.type == "PARTICLE_SYSTEM":
                if wm.attenRen_settings_particleShowEmitter and (obj.show_instancer_for_viewport != obj.show_instancer_for_render):
                    addToObjsDict = True
                    if not modifiersDict[mod]: modifiersDict[mod] = {"hide": False}
                    modifiersDict[mod]["show_emitter"] = obj
                settings = mod.particle_system.settings
                if wm.attenRen_settings_particleChildAmount and settings.child_type != "NONE" and (settings.child_nbr != settings.rendered_child_count):
                    addToObjsDict = True
                    if not modifiersDict[mod]: modifiersDict[mod] = {"hide": False}
                    modifiersDict[mod]["child_amount"] = settings
                if wm.attenRen_settings_particleDisplayPercentage and settings.display_percentage != 100:
                    addToObjsDict = True
                    if not modifiersDict[mod]: modifiersDict[mod] = {"hide": False}
                    modifiersDict[mod]["display_percentage"] = settings
        objDict["mods"] = modifiersDict

        fxsDict = {}
        if wm.attenRen_settings_gpencilShaderEffects:
            for fx in obj.shader_effects:
                if fx.show_render != fx.show_viewport:
                    addToObjsDict = True
                    fxsDict[fx] = {}
        objDict["fxs"] = fxsDict

        gpfxsDict = {}
        if wm.attenRen_settings_gpencilModifiers:
            for gpfx in obj.grease_pencil_modifiers:
                if gpfx.show_render != gpfx.show_viewport:
                    addToObjsDict = True
                    gpfxsDict[gpfx] = {}
        objDict["gpfxs"] = gpfxsDict

        if wm.attenRen_settings_instance and\
           obj.instance_type != "NONE" and\
           (obj.show_instancer_for_viewport != obj.show_instancer_for_render):
            addToObjsDict = True
            objDict["instance"] = {}
        
        if addToObjsDict:
            objsDict[obj] = objDict


    def getObjRecursively(self, collsDict, children, vl):
        for child in children:
            collDict = {"hide":False}
            objsDict = {}
            addToObjsDict = False

            for obj in child.collection.objects:
                self.objectCheck(vl, objsDict, obj)
            if bpy.context.window_manager.attenRen_settings_collVisibility:
                if self.VISIB_MODE == "EYE":
                    pass
                    # if not obj.hide_get(view_layer=vl) == obj.hide_render:
                    #     addToObjsDict = True
                elif self.VISIB_MODE == "DISPLAY":
                    pass
                    # if not obj.hide_viewport == obj.hide_render:
                    #     addToObjsDict = True
                else:
                    if (((child.hide_viewport != child.collection.hide_viewport) and child.collection.hide_render == False) or 
                        ((child.hide_viewport == child.collection.hide_viewport == False) and child.collection.hide_render == True) or
                        ((child.hide_viewport == child.collection.hide_viewport == True) and child.collection.hide_render == False)):
                        addToObjsDict = True

            if objsDict or addToObjsDict:
                collDict["objs"] = objsDict
                collsDict[child] = collDict
            if len(child.children) != 0:
                self.getObjRecursively(collsDict, child.children, vl)

    def check(self):
        scene = bpy.context.scene
        wm = bpy.context.window_manager
        self.missingFiles["hide"] = False
        self.missingFiles["files"] = [os.path.normpath(bpy.path.abspath(image.filepath)) for image in bpy.data.images if (image.filepath) and (not os.path.exists(bpy.path.abspath(image.filepath)))]\
                                        if wm.attenRen_settings_missingFiles else []
        for scene in bpy.data.scenes:
            sceneDict = {"hide":False}
            # Composite Node Check (alpha version)
            if wm.attenRen_settings_composite and scene.use_nodes:
                comp =  [node for node in scene.node_tree.nodes if node.bl_static_type == "COMPOSITE"]
                viewer =  [node for node in scene.node_tree.nodes if node.bl_static_type == "VIEWER"]
                if len(comp) == len(viewer) == 1 and len(comp[0].inputs[0].links) and len(viewer[0].inputs[0].links):
                    if comp[0].inputs[0].links[0].from_node.name != viewer[0].inputs[0].links[0].from_node.name:
                        sceneDict["composite"] = {}
            print(wm.attenRen_settings_renderRegion, scene)
            if (wm.attenRen_settings_renderRegion and
                (scene.render.border_max_x != 1. or
                scene.render.border_max_y != 1. or
                scene.render.border_min_x != 0. or
                scene.render.border_min_y != 0.)):
                sceneDict["border"] = scene.render
            if wm.attenRen_settings_resolutionPercentage and scene.render.resolution_percentage < 100:
                sceneDict["resolution_percentage"] = scene.render
            # Check if render samples are fewer than preview samples
            if wm.attenRen_settings_samples:
                if scene.render.engine == "CYCLES":
                    if scene.cycles.progressive == "PATH":
                        if scene.cycles.samples < scene.cycles.preview_samples:
                            sceneDict["cycles_sample"] = scene.render
                    elif scene.cycles.progressive == "BRANCHED_PATH":
                        if scene.cycles.aa_samples < scene.cycles.preview_aa_samples:
                            sceneDict["cycles_aa_sample"] = scene.render
                elif scene.render.engine == "BLENDER_EEVEE":
                    if scene.eevee.taa_render_samples < scene.eevee.taa_samples:
                        sceneDict["eevee_sample"] = scene.render

            vlsDict = {}
            for vl in scene.view_layers:
                vlDict = {"hide":False}
                collsDict = {}
                # This is for Scene's Master Collection
                collDict = {"hide":False}
                objsDict = {}
                for obj in vl.layer_collection.collection.objects:
                    self.objectCheck(vl, objsDict, obj)
                if objsDict:
                    collDict["objs"] = objsDict
                    collsDict[vl.layer_collection.collection] = collDict
                ### End of Master Coll Process
                # Other collections, check recursively
                self.getObjRecursively(collsDict, vl.layer_collection.children, vl)
                
                vlDict["colls"] = collsDict   
                vlsDict[vl] = vlDict
            sceneDict["view_layers"] = vlsDict
            self.checkedItems[scene] = sceneDict
        # print(self.checkedItems)
        # for coll in bpy.data.collections:
        #     if self.VISIB_MODE == "EYE":
        #         if not bpy.context.view_layer.layer_collection.children.get(coll.name).hide_viewport == coll.hide_render:
        #             self.checkedItems.add(coll)
        #     elif self.VISIB_MODE == "DISPLAY":
        #         if not coll.hide_viewport == coll.hide_render:
        #             self.checkedItems.add(coll)
        #     else:
        #         if (((bpy.context.view_layer.layer_collection.children.get(coll.name).hide_viewport != coll.hide_viewport) and coll.hide_render == False) or 
        #             ((bpy.context.view_layer.layer_collection.children.get(coll.name).hide_viewport == coll.hide_viewport == False) and coll.hide_render == True) or
        #             ((bpy.context.view_layer.layer_collection.children.get(coll.name).hide_viewport == coll.hide_viewport == True) and coll.hide_render == False)):
        #             self.checkedItems.add(coll)

        # for obj in bpy.context.scene.objects:
        #     if self.VISIB_MODE == "EYE":
        #         if not obj.hide_get() == obj.hide_render:
        #             self.checkedItems.add(obj)
        #     elif self.VISIB_MODE == "DISPLAY":
        #         if not obj.hide_viewport == obj.hide_render:
        #             self.checkedItems.add(obj)
        #     else:
        #         if (((obj.hide_get() != obj.hide_viewport) and obj.hide_render == False) or 
        #             ((obj.hide_get() == obj.hide_viewport == False) and obj.hide_render == True) or
        #             ((obj.hide_get() == obj.hide_viewport == True) and obj.hide_render == False)):
        #             self.checkedItems.add(obj)

    def matchVisibility(self, matchTo):
        """
        Collections and objects have eye's icon and display's icon. We have to consider how to cope with them.
        Statuses of display's icon and Render icon is shared among other view layers (in a same scene), 
        so process carefully when multiple view layers exist.
        match to viewport:
            if both are enabled:
                render will be enabled
            else:
                render will be disabled
                eye's and display icons will be disabled
        match to render:
            if render is enabled:
                both icons will be enabled
            else: display icons will be disabled (or user can select in preference)
                  (eye's icon has its view layer wise info, so we wouldn't like to change)
        """
        # if not self.checkedItems:
        self.check()
        for scene in self.checkedItems.values():
            for vl in scene["view_layers"].values():
                for idx, coll in enumerate(vl["colls"]):
                    if idx:
                        if matchTo == "VIEWPORT":
                            # print(coll.name,coll.hide_viewport == coll.collection.hide_viewport == False)
                            if coll.hide_viewport == coll.collection.hide_viewport == False:
                                coll.collection.hide_render = False
                            else:
                                coll.collection.hide_render = coll.hide_viewport = coll.collection.hide_viewport = True
                        elif matchTo == "RENDER":
                            if coll.collection.hide_render:
                                coll.collection.hide_viewport = True
                            else:
                                coll.hide_viewport = coll.collection.hide_viewport = False

    def saveSettings(self):
        settingFilePath = os.path.join(os.path.dirname(__file__), "attenrenSettings.txt")
        # if not os.path.exists(settingFilePath):
        types = bpy.types.WindowManager
        wm = bpy.context.window_manager
        settings = {
            types.attenRen_settings_collVisibility.keywords["attr"]: wm.attenRen_settings_collVisibility,
            types.attenRen_settings_objVisibility.keywords["attr"]: wm.attenRen_settings_objVisibility,
            types.attenRen_settings_missingFiles.keywords["attr"]: wm.attenRen_settings_missingFiles,
            types.attenRen_settings_renderRegion.keywords["attr"]: wm.attenRen_settings_renderRegion,
            types.attenRen_settings_resolutionPercentage.keywords["attr"]: wm.attenRen_settings_resolutionPercentage,
            types.attenRen_settings_samples.keywords["attr"]: wm.attenRen_settings_samples,
            types.attenRen_settings_instance.keywords["attr"]: wm.attenRen_settings_instance,
            types.attenRen_settings_modifiers.keywords["attr"]: wm.attenRen_settings_modifiers,
            types.attenRen_settings_composite.keywords["attr"]: wm.attenRen_settings_composite,
            types.attenRen_settings_particleShowEmitter.keywords["attr"]: wm.attenRen_settings_particleShowEmitter,
            types.attenRen_settings_particleChildAmount.keywords["attr"]: wm.attenRen_settings_particleChildAmount,
            types.attenRen_settings_particleDisplayPercentage.keywords["attr"]: wm.attenRen_settings_particleDisplayPercentage,
            types.attenRen_settings_gpencilModifiers.keywords["attr"]: wm.attenRen_settings_gpencilModifiers,
            types.attenRen_settings_gpencilShaderEffects.keywords["attr"]: wm.attenRen_settings_gpencilShaderEffects,
            types.attenRen_settings_autoCheck.keywords["attr"]: wm.attenRen_settings_autoCheck
        }
        with open(settingFilePath, 'w', encoding='utf-8', newline='\n') as fp:
            json.dump(settings, fp, indent=2)