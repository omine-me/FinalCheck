import bpy, os, json

class FinalCheck:
    def __init__(self):
        self.missingFiles = {}
        self.checkedItems = {}
        self.notCheckedYet = True
        """ checkedItems:
        {scenes:{
            scene1: {
                hide: True,?
                view_layers:{
                    view_layer1:{
                        hide: True,?
                        colls:{
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
        }}
        """
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
        if wm.finalCheck_prefs_objVisibility:
            if (((obj.hide_get(view_layer=vl) != obj.hide_viewport) and obj.hide_render == False) or 
                ((obj.hide_get(view_layer=vl) == obj.hide_viewport == False) and obj.hide_render == True) or
                ((obj.hide_get(view_layer=vl) == obj.hide_viewport == True) and obj.hide_render == False)):
                addToObjsDict = True
                objDict = {"hide": False}
        modifiersDict = {}
        for mod in obj.modifiers:
            if wm.finalCheck_prefs_modifiers and mod.show_render != mod.show_viewport:
                addToObjsDict = True
                modifiersDict[mod] = {"hide": False}
            if mod.type == "PARTICLE_SYSTEM":
                if wm.finalCheck_prefs_particleShowEmitter and (obj.show_instancer_for_viewport != obj.show_instancer_for_render):
                    addToObjsDict = True
                    if not mod in modifiersDict: modifiersDict[mod] = {"hide": False}
                    modifiersDict[mod]["show_emitter"] = obj
                settings = mod.particle_system.settings
                if (4, 0, 0) > bpy.app.version:
                    settings_child_percent = settings.child_nbr
                else:
                    settings_child_percent = settings.child_percent
                if wm.finalCheck_prefs_particleChildAmount and settings.child_type != "NONE" and (settings_child_percent != settings.rendered_child_count):
                    addToObjsDict = True
                    if not mod in modifiersDict: modifiersDict[mod] = {"hide": False}
                    modifiersDict[mod]["child_amount"] = settings
                if wm.finalCheck_prefs_particleDisplayPercentage and settings.display_percentage != 100:
                    addToObjsDict = True
                    if not mod in modifiersDict: modifiersDict[mod] = {"hide": False}
                    modifiersDict[mod]["display_percentage"] = settings
        objDict["mods"] = modifiersDict

        fxsDict = {}
        if wm.finalCheck_prefs_gpencilShaderEffects:
            for fx in obj.shader_effects:
                if fx.show_render != fx.show_viewport:
                    addToObjsDict = True
                    fxsDict[fx] = {}
        objDict["fxs"] = fxsDict

        gpfxsDict = {}
        # 4.3以降 grease pencilのモディファイアは通常のモディファイアと同じように扱うので、個別対応は不要
        if (4, 3, 0) > bpy.app.version:
            if wm.finalCheck_prefs_gpencilModifiers:
                for gpfx in obj.grease_pencil_modifiers:
                    if gpfx.show_render != gpfx.show_viewport:
                        addToObjsDict = True
                        gpfxsDict[gpfx] = {}
        objDict["gpfxs"] = gpfxsDict

        if wm.finalCheck_prefs_instance and\
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

            if not child.exclude:
                for obj in child.collection.objects:
                    self.objectCheck(vl, objsDict, obj)
                if bpy.context.window_manager.finalCheck_prefs_collVisibility:
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
        self.missingFiles.clear()
        self.checkedItems.clear()
        self.notCheckedYet = False
        wm = bpy.context.window_manager
        if wm.finalCheck_prefs_missingFiles:
            missingFiles = []
            op = os.path
            for image in bpy.data.images:
                if image.filepath and (not image.packed_file):
                    if image.library: ### is it a linked image?
                        try:
                            if image.filepath[:2] == "//": ### is it in same drive?
                                path = op.join(op.dirname(bpy.path.abspath(image.library.filepath)), image.filepath[2:])
                            else:
                                path = image.filepath
                            if not op.exists(path):
                                missingFiles.append(op.normpath(path))
                        except:
                            missingFiles.append("Error: Can't check this file: "+op.normpath(image.filepath))
                    else:
                        path = bpy.path.abspath(image.filepath)
                        if not op.exists(path):
                            missingFiles.append(op.normpath(path))
            if missingFiles:
                self.missingFiles["hide"] = False
                self.missingFiles["files"] = missingFiles

        for scene in bpy.data.scenes:
            if wm.finalCheck_prefs_currentScene:
                if scene.name != bpy.context.scene.name:
                    continue
            sceneDict = {}
            # Composite Node Check (alpha version)
            if wm.finalCheck_prefs_composite and scene.use_nodes:
                comp =  [node for node in scene.node_tree.nodes if node.bl_static_type == "COMPOSITE"]
                viewer =  [node for node in scene.node_tree.nodes if node.bl_static_type == "VIEWER"]
                if len(comp) == len(viewer) == 1 and len(comp[0].inputs[0].links) and len(viewer[0].inputs[0].links):
                    if comp[0].inputs[0].links[0].from_node.name != viewer[0].inputs[0].links[0].from_node.name:
                        sceneDict["composite"] = {}
            if (wm.finalCheck_prefs_renderRegion and
                (scene.render.border_max_x != 1. or
                scene.render.border_max_y != 1. or
                scene.render.border_min_x != 0. or
                scene.render.border_min_y != 0.)):
                sceneDict["border"] = scene.render
            if wm.finalCheck_prefs_resolutionPercentage and scene.render.resolution_percentage < 100:
                sceneDict["resolution_percentage"] = scene.render
            ### Check if render samples are fewer than preview samples
            if wm.finalCheck_prefs_samples:
                if scene.render.engine == "CYCLES":
                    ### version newer than 2.93.6? doesn't have progressive attribute and aa_samples
                    if (not hasattr(scene.cycles, "progressive")) or scene.cycles.progressive == "PATH":
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
                if wm.finalCheck_prefs_currentScene and wm.finalCheck_prefs_currentViewLayer:
                    if vl.name != bpy.context.view_layer.name:
                        continue
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
                
                if collsDict:
                    vlDict["colls"] = collsDict   
                    vlsDict[vl] = vlDict
            if vlsDict:
                sceneDict["view_layers"] = vlsDict
            if sceneDict:
                sceneDict["hide"] = False
                self.checkedItems[scene] = sceneDict

    def getAttr(self, prop, key):
        try:
            return prop.keywords[key]
        except AttributeError:  # blender 2.92 or before
            return prop[1][key]

    def savePrefs(self):
        prefFilePath = os.path.join(os.path.dirname(__file__), "FinalCheckPrefs.txt")
        types = bpy.types.WindowManager
        wm = bpy.context.window_manager
        prefs = {
            self.getAttr(types.finalCheck_prefs_autoCheck, 'attr'): wm.finalCheck_prefs_autoCheck,
            self.getAttr(types.finalCheck_prefs_currentScene, 'attr'): wm.finalCheck_prefs_currentScene,
            self.getAttr(types.finalCheck_prefs_currentViewLayer, 'attr'): wm.finalCheck_prefs_currentViewLayer,
            self.getAttr(types.finalCheck_prefs_collVisibility, 'attr'): wm.finalCheck_prefs_collVisibility,
            self.getAttr(types.finalCheck_prefs_objVisibility, 'attr'): wm.finalCheck_prefs_objVisibility,
            self.getAttr(types.finalCheck_prefs_missingFiles, 'attr'): wm.finalCheck_prefs_missingFiles,
            self.getAttr(types.finalCheck_prefs_renderRegion, 'attr'): wm.finalCheck_prefs_renderRegion,
            self.getAttr(types.finalCheck_prefs_resolutionPercentage, 'attr'): wm.finalCheck_prefs_resolutionPercentage,
            self.getAttr(types.finalCheck_prefs_samples, 'attr'): wm.finalCheck_prefs_samples,
            self.getAttr(types.finalCheck_prefs_instance, 'attr'): wm.finalCheck_prefs_instance,
            self.getAttr(types.finalCheck_prefs_modifiers, 'attr'): wm.finalCheck_prefs_modifiers,
            self.getAttr(types.finalCheck_prefs_composite, 'attr'): wm.finalCheck_prefs_composite,
            self.getAttr(types.finalCheck_prefs_particleShowEmitter, 'attr'): wm.finalCheck_prefs_particleShowEmitter,
            self.getAttr(types.finalCheck_prefs_particleChildAmount, 'attr'): wm.finalCheck_prefs_particleChildAmount,
            self.getAttr(types.finalCheck_prefs_particleDisplayPercentage, 'attr'): wm.finalCheck_prefs_particleDisplayPercentage,
            self.getAttr(types.finalCheck_prefs_gpencilModifiers, 'attr'): wm.finalCheck_prefs_gpencilModifiers,
            self.getAttr(types.finalCheck_prefs_gpencilShaderEffects, 'attr'): wm.finalCheck_prefs_gpencilShaderEffects
        }
        with open(prefFilePath, 'w', encoding='utf-8', newline='\n') as fp:
            json.dump(prefs, fp, indent=2)