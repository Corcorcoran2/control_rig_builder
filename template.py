import maya.cmds as cmds
import string
import maya.api.OpenMaya as om
import json
import autorig.control_rig.module.query as module_query
from PySide2.QtWidgets import QListWidget, QFileDialog

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

    try:
        with open(file_path, "w") as outfile:
            json.dump(data, outfile, indent=4)

        cmds.confirmDialog(
            title="Success",
            message=f"File saved:\n{file_path}",
            button=["OK"]
        )
    except Exception as e:
        cmds.error(f"Failed to save file: {e}")

    return data

def load_template(file_path):
    
    
    with open(file_path, "r") as f:
            data = json.load(f)
    module_list = list(data['human']['modules'].keys())
    
    #create module
    for module in module_list:
        module_cls = module_query.find_cls_module(module)
        module_instance = module_cls.create_from_name(module)
        module_instance.create_module()

    for module in module_list:    
        module_cls = module_query.find_cls_module(module)
        module_instance = module_cls.create_from_name(module)
        
        features = data['human']['modules'][module]['features']
        for feature in features:
            print(module, feature)
            module_instance.add_feature(feature)
    
        inputs = data['human']['modules'][module]['inputs']
        if inputs:
            for input in inputs:
                input_module_cls = module_query.find_cls_module(input)
                input_module_instance = input_module_cls.create_from_name(input)
                
                module_instance.add_module_connection(input_module_instance,module_instance)
