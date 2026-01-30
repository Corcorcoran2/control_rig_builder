#Example FK feature composed into the modules that can create an FK control chain

import autorig.control_rig.module.utils as module_utils
import autorig.control_rig.feature.FK_utils as FK_utils

from autorig.control_rig.feature.base import FeatureBase

class FeatureFK(FeatureBase):
    feature_name = "FK"

    def create(self, instance_module, ID_list):
        root_loc,link_data = self.create_chain(instance_module, ID_list)        
        self.parent_FK_nodes(root_loc,link_data)

    def create_chain(self, instance_module, ID_list):       
        root_loc, link_data = FK_utils.create_FK_chain(ID_list, 
                                    aim_direction = 1,
                                    module_name=instance_module.instance_module_name,
                                    )
        return root_loc, link_data
        
    def parent_FK_nodes(self,root_loc,link_data):
        FK_utils.parent_FK_nodes(root_loc,link_data)      
