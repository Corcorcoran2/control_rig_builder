#Base class to all modules that can be used to rig creatures in my pipeline.

from typing import List, Dict
from abc import ABC, abstractmethod

import autorig.control_rig.module.error as module_error
import autorig.control_rig.module.setup as module_setup
import autorig.control_rig.feature.base as feature_base

from autorig.control_rig.module.registry import MODULE_REGISTRY

class ModuleBase(ABC):
    cls_module_name = ""
    
    @property
    def instance_module_name(self) -> str:
        if self.side:
            return f"{self.cls_module_name}_{self.side}"
        else:
            return self.cls_module_name
    
    @property
    def cls_module_name(cls) -> str:
        return cls.cls_module_name
    
    @property
    def allow_input(self) -> bool:
        return True
    
    @property
    def allow_output(self) -> bool:
        return True
    
    @property
    @abstractmethod
    def ID_list(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def supported_features(self) -> Dict[feature_base.FeatureBase,List[str]]:
        pass
    
    @property
    @abstractmethod
    def supported_multi_features(self) -> Dict[feature_base.FeatureBase,List[str]]:
        pass

    @property
    @abstractmethod
    def attach_key(self) -> Dict[str, str]:
        pass

    def __init__ (self, side="", *args, **kwargs):
        self.side = side
        self.initialized_features = {}
        self.initialized_multi_features = {}
        self.initialize_features()
        self.initialize_multi_features()

    #Class modules placed in the module package of the tool are registered at runtime to a dictionary.
    #This can be accessed by the Module Builder UI to get human-readable module names and create module instances.
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
    
    @classmethod
    def create_from_name(cls, name: str):
        side = name.rsplit("_", 1)[-1] if "_" in name else ""
        return cls(side=side)
    
    @abstractmethod
    def add_feature(self, feature):
        raise NotImplementedError("ABSTRACT METHOD: add_feature must contain logic for adding module features")
    
    @abstractmethod
    def remove_feature(self, feature):
        raise NotImplementedError("ABSTRACT METHOD: remove_feature must contain logic for removing module features")

    def initialize_features(self):
        for feature_cls in self.supported_features:
            feature = feature_cls(self)
            self.initialized_features[feature.feature_name] = feature
        
    def initialize_multi_features(self):
        if self.supported_multi_features:
            for feature_cls in self.supported_multi_features:
                feature = feature_cls(self)
                self.initialized_multi_features[feature.feature_name] = feature
    
    #Make nodes for module systems

    def validate_bind_joints(self):
        is_valid = module_setup.get_bind_joints(self.instance_module_name)   
        return is_valid
    
    def create_module(self):
        is_valid = self.validate_bind_joints()
        if not is_valid:
            return

        self.create_module_group_nodes()
        self.create_driver_joints()
        self.create_module_root_guide()
          
    def create_driver_joints(self):
        module_setup.create_driver_joints(self)

    def create_module_root_guide(self):
        module_setup.create_module_end_guides(self)

    def create_module_group_nodes(self):
        module_setup.create_module_group_nodes(self.instance_module_name)    

    def add_feature(self,feature):
        instance_feature = self.initialized_features.get(feature)
        if instance_feature:
            ID_list = self.supported_features[type(instance_feature)]
            instance_feature.create(self,ID_list)
            self.add_module_attr(feature, "moduleFeatures")
            instance_feature.attach(self)
        elif self.initialized_multi_features.get(feature):
            instance_feature = self.initialized_multi_features.get(feature)
            kwargs = self.supported_multi_features[type(instance_feature)]
            instance_feature.create(self,**kwargs)
        else:
            module_error.send_warning(f"Feature {feature} not supported by {self.cls_module_name} class.")

    def remove_feature(self,feature):
        instance_feature = self.initialized_features.get(feature)
        if instance_feature:
            self.supported_features[type(instance_feature)]
            
            instance_feature.remove()
        else:
            module_error.send_warning(f"Feature not supported by {self.cls_module_name} class.")
   