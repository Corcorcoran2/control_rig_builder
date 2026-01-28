import autorig.control_rig.module.base
from autorig.control_rig.module.base import ModuleBase
import autorig.control_rig.module.query as module_query
import autorig.control_rig.module.utils as module_utils
from autorig.control_rig.feature.FK import FeatureFK
from autorig.control_rig.feature.IK import FeatureIK
import autorig.control_rig.feature.foot_roll
from autorig.control_rig.feature.foot_roll import FeatureFootRoll
import autorig.control_rig.feature.switch as feature_switch
import maya.cmds as cmds
import importlib
importlib.reload(autorig.control_rig.feature.foot_roll)
importlib.reload(autorig.control_rig.module.base)
importlib.reload(module_utils)
importlib.reload(module_query)
importlib.reload(autorig.control_rig.feature.IK)

class ModuleHumanLeg(ModuleBase):
    cls_module_name = "human_leg"
    
    def __init__ (self, side, *args, **kwargs):
        super().__init__(side=side,*args, **kwargs)    

    @property
    def ID_list(self):
        return [f"leg_{self.side}_1",f"leg_{self.side}_2",f"leg_{self.side}_3"]
    
    @property
    def supported_features(self):
        return {FeatureFK: self.ID_list,
                FeatureIK: self.ID_list
                }
    
    @property
    def supported_multi_features(self):
        return {FeatureFootRoll: {
                "ball": True,
                "toe": False,
                "heel": False
                }
        }
    
    @property
    def attach_key(self):
        return {"human_spine_M": "spine_M_1"}
    
    def add_feature(self,feature):
        super().add_feature(feature)
        if feature == "FK" or feature == "IK":
            self.check_switch()
    
    def check_switch(self):
        features = cmds.getAttr(f"{self.instance_module_name}.moduleFeatures")
        if "IK" in features and "FK" in features:
            self.create_switch()
    
    def create_switch(self):
        ctrl, loc = feature_switch.make_switch(self.ID_list, self.instance_module_name)

        cmds.parent(ctrl, f"{self.instance_module_name}|control")
        cmds.parent(loc, f"{self.instance_module_name}|guide")

        feature_switch.add_driver_switch(self.instance_module_name)

if __name__ == "__main__":
    import maya.cmds as cmds

    current_scene = cmds.file(q=True, sn=True)

    if current_scene:
        cmds.file(current_scene, o=True, force=True)
    else:
        cmds.file(new=True, force=True)

    instance = ModuleHumanLeg('L')
    instance.create_module()
    instance.add_feature("IK")
    instance.add_feature("FK")
