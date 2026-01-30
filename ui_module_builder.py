#Module Builder UI from my Character Rigging Pipeline. To promote structure and organization, UI classes do not import
#cmds or OpenMaya, instead only handling PySide related functionality. Maya specific logic exists in various helper packages.

#UI initialization abridged for brevity.

from PySide2.QtWidgets import QListWidget, QFileDialog, QWidget, QLabel, QVBoxLayout, QHBoxLayout

from common.ui.base import UIBase
import common.ui.widget as widgets

import autorig.control_rig.module.query as module_query
import autorig.control_rig.module.registry as module_registry
import autorig.control_rig.module.skeleton as module_skeleton 
import autorig.control_rig.module.template as module_template
import autorig.control_rig.module.error as module_error

from autorig.control_rig.module_builder.ui.edit_module import EditModule


class ModuleBuilder(UIBase):
    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected_module=None
        self.module_instance = None
        self.create_widgets()
        self.create_layouts()
        self.populate_modules_from_scene()
        module_registry.register_modules()

    #PySide UI tools in my pipelines extend a base class that reinforces abstract properties to make sure basic
    #attributes are always initialized.

    @property
    def window_title(self) -> str:
        return "Module Builder"

    @property
    def window_width(self) -> float:
        return 1000

    @property
    def window_height(self) -> float:
        return 500
    
    #The widgets module holds functions that improve readability for the creation of PySide widgets and layouts.

    def create_widgets(self):
        self.module_list_label = QLabel("Modules in Scene")
        
        self.module_list = QListWidget()
        self.module_list.itemClicked.connect(self.on_module_clicked)
        
        self.module_input_label = QLabel("Upstream Inputs")
        
        self.module_input_list = QListWidget()
        self.module_input_list.itemClicked.connect(self.on_input_clicked)

        self.input_add_button = widgets.initialize_button_widget("Add", self.open_add_input, enabled=False)

        self.input_remove_button = widgets.initialize_button_widget("Remove", self.remove_input, enabled=False)

        self.module_features_label = QLabel("Features")
        
        "...More Widgets..."
    
    def create_layouts(self):
        module_select_layout = widgets.initialize_layout(
            layout_type = QVBoxLayout(),
            widgets = [self.module_list_label,
                       self.module_list,
                       ]
        )

        module_input_buttons_layout = widgets.initialize_layout(
            layout_type = QHBoxLayout(),
            widgets = [self.input_add_button,
                       self.input_remove_button]
        )
        
        module_input_layout = widgets.initialize_layout(
            layout_type = QVBoxLayout(),
            widgets = [self.module_input_label,
                       self.module_input_list,
                       module_input_buttons_layout]
        )

        module_features_buttons_layout = widgets.initialize_layout(
            layout_type = QHBoxLayout(),
            widgets = [self.features_add_button,
                       self.features_remove_button]
        )
        
        module_features_layout = widgets.initialize_layout(
            layout_type = QVBoxLayout(),
            widgets = [self.module_features_label,
                       self.module_features_list,
                       module_features_buttons_layout]
        )

        "...More Layouts..."

        main_layout = widgets.initialize_layout(
            layout_type = QHBoxLayout(),
            widgets = [module_select_layout,
                       right_layout
                       ],
            stretch=True
        )                 

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def enable_create_module_button(self):
        self.features_add_button.setEnabled(True)

    def enable_add_buttons(self):
        self.input_add_button.setEnabled(True)      
        self.output_add_button.setEnabled(True)
    
    def disable_edit_buttons(self):
        self.input_add_button.setEnabled(False)       
        self.output_add_button.setEnabled(False)
        self.input_remove_button.setEnabled(False)
        self.features_remove_button.setEnabled(False)
        self.output_remove_button.setEnabled(False)

    def clear_module_lists(self):
        self.module_features_list.clear()
        self.module_input_list.clear()
        self.module_output_list.clear()
    
    def set_add_feature_function(self, function):
        if function == "Create":
            self.features_add_button.setText("Create")
            self.features_add_button.clicked.disconnect()
            self.features_add_button.clicked.connect(self.create_module)
        elif function == "Add":
            self.features_add_button.setText("Add")
            self.features_add_button.clicked.disconnect()
            self.features_add_button.clicked.connect(self.open_add_feature)

    def on_module_clicked(self, item):
        self.clear_module_lists()
        self.disable_edit_buttons()
        
        self.selected_module = item.text()

        module_cls = module_query.find_cls_module(self.selected_module)
        self.module_instance = module_cls.create_from_name(self.selected_module) 
        
        module_parent_node = module_query.find_single_node(attrs = {
            "moduleType": self.selected_module
        })
        
        if not module_parent_node:
            self.set_add_feature_function("Create")
            self.enable_create_module_button()
            return
                    
        self.set_add_feature_function("Add")
        self.enable_add_buttons()
        attributes = [
            ("moduleFeatures", self.module_features_list),
            ("inputModule", self.module_input_list),
            ("outputModules", self.module_output_list),
        ]

        for attr_name, ui_list in attributes:
            value = module_query.find_rig_attribute(node_name=module_parent_node, attr=attr_name)
            if value:
                self.populate_module_list(value, ui_list)

    def on_input_clicked(self):
        self.input_remove_button.setEnabled(True)

    def on_feature_clicked(self):
        self.features_remove_button.setEnabled(True)

    def on_output_clicked(self):
        self.output_remove_button.setEnabled(True)

    def populate_module_list(self,items,module_list):
        items = items.split(";")
        [module_list.addItem(item) for item in items if item]

    def populate_modules_from_scene(self):
        bind_joints = module_query.find_multiple_nodes(attrs = {
            "featureType": "bind_joint"
        })

        for joint in bind_joints:
            module_parent = module_query.find_rig_attribute(node_name = joint,
                                 attr = "moduleParent")
            if not module_parent in [self.module_list.item(i).text() for i in range(self.module_list.count())]:
                self.module_list.addItem(module_parent)

    def create_module(self):
        self.module_instance.create_module()

        self.features_add_button.setText("Add")
        self.features_add_button.clicked.disconnect()
        self.features_add_button.clicked.connect(self.open_add_feature)

        self.enable_add_buttons()

    def open_add_feature(self):
        potential_feature_list = self.module_instance.initialized_features.keys()

        existing_features = [self.module_features_list.item(i).text() 
                             for i in range(self.module_features_list.count())]
        
        feature_list = [
            feature for feature in potential_feature_list
            if feature not in existing_features]
        
        potential_multi_feature_list = self.module_instance.initialized_multi_features.keys()

        if potential_multi_feature_list:
            for feature in potential_multi_feature_list:
                if feature not in existing_features:
                    feature_list.append(feature)

        if feature_list:
            features_ui = EditModule('Features', feature_list)
            features_ui.confirmed_features.connect(self.add_feature)
        else:
            module_error.send_warning("No remaining module features.")

    def add_feature(self, features):
        for feature in features:
            self.module_instance.add_feature(feature)
            self.module_features_list.addItem(feature)

    def remove_feature(self):              
        if not self.module_features_list.count():
            self.module_instance.remove_module()
            self.set_add_feature_function("Create")
            return

        selected_feature = self.module_features_list.selectedItems()[0].text()            
        self.module_instance.remove_feature(selected_feature)
        for i in range(self.module_features_list.count()):
            if self.module_features_list.item(i).text() == selected_feature:
                self.module_features_list.takeItem(i)
                break

        self.features_remove_button.setEnabled(False)      

    def open_add_input(self):
        if not self.module_instance.allow_input:
            module_error.send_warning(f"Module '{self.module_instance.instance_module_name}' does not allow an input.")
            return
        
        existing_input = module_query.find_rig_attribute("inputModule", self.module_instance.instance_module_name)
        
        if existing_input:
            module_error.send_warning(f"Module '{self.module_instance.instance_module_name}' already has an input.")
            return
                
        module_nodes = module_query.find_multiple_nodes({
        "featureType": "module_group"
        })

        potential_input_list = [module_query.find_rig_attribute(node_name = node, attr = "moduleType")
                                for node in module_nodes
                                if self.module_instance.instance_module_name not in node]

        if not potential_input_list:
            module_error.send_warning("No other modules exist in scene.")
            return

        input_ui = EditModule('Input', potential_input_list)
        input_ui.confirmed_features.connect(self.add_input)            
        
    def add_input(self, inputs):
        base_instance = self.module_instance
        
        input_cls = module_query.find_cls_module(inputs[0])
        input_instance = input_cls.create_from_name(inputs[0]) 
        
        base_instance.add_module_connection(input_instance,base_instance)

        self.module_input_list.clear()
        self.module_input_list.addItem(input_instance.instance_module_name)
          
    def remove_input(self):
        base_instance = self.module_instance
        
        input_cls = module_query.find_cls_module(self.module_input_list.selectedItems()[0].text())
        input_instance = input_cls.create_from_name(self.module_input_list.selectedItems()[0].text())

        if base_instance.allow_input:           
            base_instance.remove_module_connection(input_instance,base_instance)

        input_instance.remove_output_attr(base_instance.instance_module_name)
        base_instance.remove_input_attr()

        for i in range(self.module_input_list.count()):
            if self.module_input_list.item(i).text() == input_instance.instance_module_name:
                self.module_input_list.takeItem(i)
                break

        self.input_remove_button.setEnabled(False) 

    def open_add_output(self):
        if not self.module_instance.allow_output:
            module_error.send_warning(f"Module '{self.module_instance.instance_module_name}' is not allowed to output.")
            return
        
        module_nodes = module_query.find_multiple_nodes({
        "featureType": "module_group"
        })
        
        if not module_nodes:
            module_error.send_warning("No modules exist in scene.")
            return
        
        potential_output_list = []

        for node in module_nodes:                    
            existing_input = module_query.find_rig_attribute(node_name = node,
                            attr = "inputModule")

            if existing_input:
                continue

            module_type = module_query.find_rig_attribute(node_name = node,
                            attr = "moduleType")
            
            potential_output_cls = module_query.find_cls_module(module_type)
            potential_output_instance = potential_output_cls.create_from_name(module_type) 

            if not self.module_instance.instance_module_name == module_type and potential_output_instance.allow_input:
                potential_output_list.append(module_type)
        
        if not potential_output_list:
            module_error.send_warning("No compatible modules exist in scene.")
            return
        
        features_ui = EditModule('Output', potential_output_list)
        features_ui.confirmed_features.connect(self.add_output)

    def add_output(self, outputs):
        base_instance = self.module_instance
        
        output_cls = module_query.find_cls_module(outputs[0])
        output_instance = output_cls.create_from_name(outputs[0]) 

        output_instance.add_module_connection(base_instance,output_instance)

        module_outputs = module_query.find_rig_attribute(node_name = base_instance.instance_module_name,
                                 attr = "outputModules")
        self.module_output_list.clear()
        self.populate_module_list(module_outputs,self.module_output_list)

    def remove_output(self):
        base_instance = self.module_instance
        
        output_cls = module_query.find_cls_module(self.module_output_list.selectedItems()[0].text())
        output_instance = output_cls.create_from_name(self.module_output_list.selectedItems()[0].text())

        if base_instance.allow_output:           
            base_instance.remove_module_connection(base_instance,output_instance)

        base_instance.remove_output_attr(output_instance.instance_module_name)
        output_instance.remove_input_attr()

        for i in range(self.module_output_list.count()):
            if self.module_output_list.item(i).text() == output_instance.instance_module_name:
                self.module_output_list.takeItem(i)
                break

        self.output_remove_button.setEnabled(False)

    def load_template(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Rig Template",
            "",
            "JSON Files (*.json)"
        )        
        
        module_template.load_template(file_path)

    def save_as_template(self):
        module_template.save_as_template("human")

    def attach_bind(self):
        module_skeleton.connect_bind_skeleton()

    def detach_bind(self):
        module_skeleton.disconnect_bind_skeleton()

