[My website](www.jaspercorcoran.com)

# control_rig_builder
This breakdown will cover more of the Python and Software Design aspects of my control rig pipeline tools.

For my pipeline tools I am above all designing with the goal to make the tool easy to use by artists, and easy to extend by programmers. Project goals and requirements vary widely, so tools planned for adaptability and longevity are most likely to be kept and used in a pipeline.

## Overview
My control rig tools are built on the idea of modularity. I am not thinking of rigs in terms of human or cat, but in terms of Arm, Leg, Tail, etc. This allows the overhead work done for each of these sections of the rig to be usable in other projects that are not as simple as a generic character.

Modules keep the majority of their data private. Any data that must be moved in or out of a module is done so with designated input and output NULL nodes that will take specific matrices and pass them along. This makes a predictable reference point for where data should be accessed between classes.

All of the logic is completely based on matrix math and matrix nodes. No Maya native constraints are used, allowing for performance boosts from node editor decluttering and flat DAG hierarchies.

Nodes are assigned custom string attributes when they are created so that they are specifically tagged as part of my rigging system. Instead of generically iterating a list of joints from cmds.ls("joint"), I can use a helper function that uses OpenMaya to find a joint specifically tagged with the "FeatureType" attribute "bind_joint." This makes it so that accidental name changes to nodes in the outliner do not ruin any logic that would otherwise need to find the node by its string name.

## PySide UI

The majority of my tools are packaged into PySide2 UIs designed under the assumption that the user will not be expected to interact with the underlying Python logic. I've worked with control rig systems that did not have a user interface, so creating a rig required scripting familiarity and the need to dig through the documentation to get up and running. In my tool, interactions with the UI essentially build out the Python script by choosing functions and class instances, allowing the rigs to exist as exportable and writable templates behind the scenes (more on that later).

I am taking advantage of class inheritance throughout this tool, my UIs being the first of these parent child hierarchies. I have a base class that extends the QMainWindow, and is a module that is common to all of my tools to make default parameters predictable in all of my tools. Based on a GDC talk from Muhammad Bin Tahir Mir, I enforce abstract class decorators and NotImplementedError where possible. This makes it so if a developer wants to make a new tool in my pipeline, there are basic parameters that are needed that create a sense of uniformity with all tools.

As a general design rule, I have made it a goal to have no cmds or OpenMaya imports in any of my UIs. This forces a decoupling of responsibility, where UI classes are only dealing with PySide2 widgets and commands, and any maya related functionality is passed on to helper modules. I find this sets a good standard for what the UI class is actually responsible for.

## Designing for Developer Extensibility
At a high level the first major task was determining how I was going to get the UI to register its database of modules. To do this, I have a dictionary called MODULE_REGISTRY that is given a key-value pair for every module in the designated directory. This is populated when each class in the directory is imported at runtime, and my base module class will append the dictionary when the subclass is initialized:

```python 
def __init_subclass__(cls, **kwargs):
        if cls is ModuleBase:
            return

        if not isinstance(getattr(cls, "cls_module_name", None), str):
            raise TypeError(
                f"{cls.__name__} must define a class attribute 'cls_module_name' with str value (ex. human_arm)"
            )
        type = getattr(cls, "cls_module_name", None)
        if type:
            MODULE_REGISTRY[type] = cls
```
The class can then be accessed by the name in the dictionary by querying the MODULE_REGISTRY dictionary.

The module classes themselves are only responsible for the creation and deletion of a driver joint chain hierachy and organizational group nodes. Any control-based driver logic is added through composition of feature classes like FK, IK, etc. These are defined in class properties:

*From ModuleLeg*
```python
@property
    def supported_features(self):
        return {FeatureFK: self.ID_list,
                FeatureIK: self.ID_list
                }
```

The creator of the module is responsible for giving the feature class as the key, and the desired ID range as the values. The ID range is the expected string prefix for all associated nodes in the class. In the case of the arm, there are the clavicle, shoulder, elbow, and wrist joint. Since the FK feature would need to be added at all 4, and the RPIK Feature to just the last 3, you would add the dictionary key-value pair as "_FeatureIK: self.ID_list[1:]". By fully separating Maya driver logic into separate classes, they can be reused in a cleaner fashion than multi-layered subclasses in the BaseModule inheritance chain.

Say for example you wanted to add a new module to the rigging pipeline. You can take a templated file that adds headers for the necessary properties and methods the programmer must define (these are enforced with abc, similar to what I described for my UI class). The programmer would add the features they want to support to the supported_features property, and then place the module in the designated module folder. Once this is complete, the UI is compatible with the module, and creation options will be shown in the UI if the proper bind joints exist in the current scene.

## Designing for Artists
Although any _new_ rig logic or modules must be added through Python extension, the rigging artist is able to package their work into reusable templates, with the template.py features called by the UI template buttons. If the artist is working on a generic human skeleton that is expected to be a base for all humans in the project, any rig logic can be saved out to a .json file, to be applied at a later date. Since the only pre-requisite for the Module Builder is the existence of properly tagged bind joints, any character that reuses the skeleton can have the same rig logic instantly added.

```Python
def save_as_template(template_name):
    file_path, _ = QFileDialog.getSaveFileName(
            None,
            "Save Rig Template",
            "",                     
            "JSON Files (*.json)"   
        )

    if not file_path:
        return

    if not file_path.lower().endswith(".json"):
        file_path += ".json"
    
    data = {}
    
    data[template_name] = {}
    data[template_name]["modules"] = {}

    for n in cmds.ls(type="transform"):
        if not "joint" in n:
            if cmds.objExists(f"{n}.moduleType"):
                data[template_name]["modules"][cmds.getAttr(f"{n}.moduleType")] = {}
                
                features = cmds.getAttr(f"{n}.moduleFeatures")
                if features:
                    features_list = [f for f in features.split(";") if f]
                else:
                    features_list = []
                
                inputs = cmds.getAttr(f"{n}.inputModule")
                if inputs:
                    inputs_list = [i for i in inputs.split(";") if i]
                else:
                    inputs_list = []


                outputs = cmds.getAttr(f"{n}.outputModules")
                if outputs:
                    outputs_list = [o for o in outputs.split(";") if o]
                else:
                    outputs_list = []
                
                data[template_name]["modules"][cmds.getAttr(f"{n}.moduleType")]["features"] = features_list
                data[template_name]["modules"][cmds.getAttr(f"{n}.moduleType")]["inputs"] = inputs_list
                data[template_name]["modules"][cmds.getAttr(f"{n}.moduleType")]["outputs"] = outputs_list
```

This same idea is used again in my Shape Factory. If the rigging artist has settled on a shape language and color scheme they would like to standardize, the NURBS data can be saved to a .json as well. Each curve will then be rebuilt with OpenMaya based on the recorded CV, Knot, From, and Degree.



