#Example implementation of the ModuleLeg class inheriting from ModuleBase. Actual node creation and
#Maya specific logic is handled by feature classes through composition.

import maya.cmds as cmds

from autorig.control_rig.module.base import ModuleBase
from autorig.control_rig.feature.FK import FeatureFK
from autorig.control_rig.feature.IK import FeatureIK
from autorig.control_rig.feature.foot_roll import FeatureFootRoll

import autorig.control_rig.module.query as module_query
import autorig.control_rig.module.utils as module_utils
import autorig.control_rig.feature.switch as feature_switch

class ModuleHumanLeg(ModuleBase):
    #Name is defined at class level to be added to MODULE_REGISTRY for UI detection.
    cls_module_name = "human_leg"
    
    def __init__ (self, side, *args, **kwargs):
        super().__init__(side=side,*args, **kwargs)    

    #Expected node name pattern to be suffixed for driver joints, FK, IK, etc.
    @property
    def ID_list(self):
        return [f"leg_{self.side}_1",f"leg_{self.side}_2",f"leg_{self.side}_3"]
    
    #Compatible feature classes specified here along with ID list range to apply the system.
    @property
    def supported_features(self):
        return {FeatureFK: self.ID_list,
                FeatureIK: self.ID_list
                }
    
    #Features that require multiple modules built have additional checks to make sure they exist in scene.
    #For example FeatureFootRoll can only be added to the rig if HumanLeg and HumanFoot are created first.
    @property
    def supported_multi_features(self):
        return {FeatureFootRoll: {
                "ball": True,
                "toe": False,
                "heel": False
                }
        }
    
    #Module will attach to final joint of upstream module unless specified here.
    @property
    def attach_key(self):
        return {"human_spine_M": "spine_M_1"}
    
    #ModuleLeg has additional checks in place to allow addition and removal of a switch system.
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
